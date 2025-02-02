import pretty_midi

# Limit note range for specific instruments
def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

# Create and populate pretty_midi instruments
def create_and_assign_instruments_dynamic(layer_notes, instrument_combos, combo1_duration=16, combo2_duration=8):
    """
    Assigns notes to instruments dynamically based on their start time.
    
    Args:
        layer_notes (dict): Keys are layer names (e.g., "melody") and values are lists of note dicts.
        instrument_combos (dict): A dictionary containing both combo mappings.
            For example:
            {
              "combo1": {
                  "melody": ("Violin", 55, 103),
                  "harmony": ("French Horn", 36, 65),
                  "rhythm": ("Timpani", 29, 51),
              },
              "combo2": {
                  "melody": ("Flute", 60, 96),
                  "harmony": ("Clarinet", 48, 72),
                  "rhythm": ("Bass", 28, 52),
              },
            }
        combo1_duration (int): Number of beats to use combo1.
        combo2_duration (int): Number of beats to use combo2.
        
    Returns:
        Tuple[List[pretty_midi.Instrument], List[Dict]]:
            - A list of PrettyMIDI Instrument objects.
            - A list of note dicts that were assigned.
    """
    instruments_dict = {}  # key: (layer, combo_id), value: pretty_midi.Instrument
    orchestration_notes = []
    
    for layer, notes in layer_notes.items():
        for note in notes:
            # Determine which combo to use based on note start time
            combo_id = get_combo_for_beat(note['start'], combo1_duration, combo2_duration)
            # Get the instrument info for this layer from the chosen combo.
            inst_info = instrument_combos[combo_id][layer]  # e.g., ("Violin", 55, 103)
            inst_name, min_pitch, max_pitch = inst_info
            
            # Filter the note if it's out of the instrument's range.
            if note['pitch'] < min_pitch or note['pitch'] > max_pitch:
                continue  # Skip this note
            
            # Mark the note with the instrument name (optional, for bookkeeping).
            note['instrument'] = inst_name
            
            # Use a key (layer, combo_id) so that notes in the same time segment get the same instrument.
            key = (layer, combo_id)
            if key not in instruments_dict:
                # Create a new PrettyMIDI Instrument object.
                program = pretty_midi.instrument_name_to_program(inst_name)
                instrument_obj = pretty_midi.Instrument(program=program, name=f"{inst_name}_{layer}_{combo_id}")
                instruments_dict[key] = instrument_obj
            
            # Create a PrettyMIDI note and add it to the appropriate instrument.
            pm_note = pretty_midi.Note(
                velocity=note['velocity'],
                pitch=note['pitch'],
                start=note['start'],
                end=note['end']
            )
            instruments_dict[key].notes.append(pm_note)
            orchestration_notes.append(note)
    
    # Return the list of instrument objects and the orchestration notes.
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

