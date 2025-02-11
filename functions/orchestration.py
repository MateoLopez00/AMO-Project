import pretty_midi

# Limit note range for specific instruments
def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

# Create and populate pretty_midi instruments
def create_and_assign_instruments_dynamic(layer_notes, instrument_combos, combo1_duration=16, combo2_duration=8):
    instruments_dict = {}  # Key: (layer, combo_id, inst_name), Value: PrettyMIDI Instrument object
    orchestration_notes = []

    for layer, notes in layer_notes.items():
        for note in notes:
            # Determine the current combo based on the note's start time.
            combo_id = get_combo_for_beat(note['start'], combo1_duration, combo2_duration)
            # Get the list of candidate instruments for this layer in the current combo.
            candidate_instruments = instrument_combos[combo_id][layer]
            
            # For Option A, assign the note to every candidate instrument whose range covers the note.
            for inst_info in candidate_instruments:
                inst_name, min_pitch, max_pitch = inst_info
                
                # Check if the note's pitch falls within the candidate instrument's range.
                if min_pitch <= note['pitch'] <= max_pitch:
                    # Create a unique key based on layer, combo, and instrument name.
                    key = (layer, combo_id, inst_name)
                    if key not in instruments_dict:
                        # Create a PrettyMIDI instrument object using the valid instrument name.
                        program = pretty_midi.instrument_name_to_program(inst_name)
                        instrument_obj = pretty_midi.Instrument(program=program, name=f"{inst_name}_{layer}_{combo_id}")
                        instruments_dict[key] = instrument_obj

                    # Create a PrettyMIDI note and add it to this instrument.
                    pm_note = pretty_midi.Note(
                        velocity=note['velocity'],
                        pitch=note['pitch'],
                        start=note['start'],
                        end=note['end']
                    )
                    instruments_dict[key].notes.append(pm_note)
            
            # Optionally, add the note to orchestration_notes once (for evaluation/visualization),
            # even though it may be played by multiple instruments.
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

