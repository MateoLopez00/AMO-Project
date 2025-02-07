import pretty_midi

# Limit note range for specific instruments
def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

# Create and populate pretty_midi instruments
def create_and_assign_instruments_dynamic(layer_notes, instrument_combos, combo1_duration=16, combo2_duration=8):
    instruments_dict = {}
    orchestration_notes = []

    for layer, notes in layer_notes.items():
        for note in notes:
            combo_id = get_combo_for_beat(note['start'], combo1_duration, combo2_duration)
            inst_info = instrument_combos[combo_id][layer]  # e.g., ("Violin", 55, 103)
            inst_name, min_pitch, max_pitch = inst_info

            # Check if the note is below the current instrument's range.
            if note['pitch'] < min_pitch:
                # Reassign to a valid low instrument, "Contrabass", which is recognized by Pretty MIDI.
                inst_name = "Contrabass"
                # Define an extended lower range for Contrabass, for example:
                min_pitch, max_pitch = 20, 60

            # Optionally, you can also check if note['pitch'] > max_pitch if needed.
            note['instrument'] = inst_name

            # Include instrument name in the key to distinguish instruments if needed.
            key = (layer, combo_id, inst_name)
            if key not in instruments_dict:
                program = pretty_midi.instrument_name_to_program(inst_name)
                instrument_obj = pretty_midi.Instrument(program=program, name=f"{inst_name}_{layer}_{combo_id}")
                instruments_dict[key] = instrument_obj

            pm_note = pretty_midi.Note(
                velocity=note['velocity'],
                pitch=note['pitch'],
                start=note['start'],
                end=note['end']
            )
            instruments_dict[key].notes.append(pm_note)
            orchestration_notes.append(note)

    return list(instruments_dict.values()), orchestration_notes


def get_combo_for_beat(beat, combo1_duration=16, combo2_duration=8):
    """
    Given a beat value, decide which combo to use.
    The pattern is: first combo1_duration beats use "combo1", 
    then the next combo2_duration beats use "combo2", repeating.
    """
    cycle_length = combo1_duration + combo2_duration  # e.g., 24 beats
    position_in_cycle = beat % cycle_length
    if position_in_cycle < combo1_duration:
        return "combo1"
    else:
        return "combo2"

