import pretty_midi

# Define a desired channel mapping for instruments.
desired_channels = {
    'Violin': 1,
    'Viola': 2,
    'Cello': 3,
    'Bass': 4,           # For example, if you use "Bass" to mean Acoustic Bass.
    'Flute': 5,
    'Oboe': 6,
    'Clarinet': 7,
    'Bassoon': 8,
    'French Horn': 9,
    'Trumpet': 10
}

def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

def create_and_assign_instruments_dynamic(layer_notes, instrument_combos, combo1_duration=16, combo2_duration=8):
    instruments_dict = {}  # Key: (layer, combo_id, inst_name) --> value: PrettyMIDI Instrument object
    orchestration_notes_detailed = []  # We'll store note info with assigned channels here.
    
    for layer, notes in layer_notes.items():
        for note in notes:
            # Create a dictionary to hold the note data and a list for channels assigned.
            note_dict = {
                'pitch': note['pitch'],
                'start': note['start'],
                'end': note['end'],
                'velocity': note['velocity'],
                'assigned_channels': []  # Will be filled with channels from candidate instruments.
            }
            
            # Determine active combo based on the note's start time.
            combo_id = get_combo_for_beat(note['start'], combo1_duration, combo2_duration)
            candidate_instruments = instrument_combos[combo_id][layer]
            
            for inst_info in candidate_instruments:
                inst_name, min_pitch, max_pitch = inst_info
                if min_pitch <= note['pitch'] <= max_pitch:
                    key = (layer, combo_id, inst_name)
                    if key not in instruments_dict:
                        program = pretty_midi.instrument_name_to_program(inst_name)
                        instrument_obj = pretty_midi.Instrument(
                            program=program,
                            name=f"{inst_name}_{layer}_{combo_id}",
                            is_drum=False
                        )
                        # Assign channel based on our desired mapping.
                        instrument_obj.channel = desired_channels.get(inst_name, 0)
                        instruments_dict[key] = instrument_obj
                    # Append the channel from this candidate instrument to the note's list.
                    note_dict['assigned_channels'].append(instruments_dict[key].channel)
                    
                    pm_note = pretty_midi.Note(
                        velocity=note['velocity'],
                        pitch=note['pitch'],
                        start=note['start'],
                        end=note['end']
                    )
                    instruments_dict[key].notes.append(pm_note)
            # Append the detailed note record after processing candidates.
            orchestration_notes_detailed.append(note_dict)
    
    # Return both the instrument objects and the detailed orchestration notes.
    return list(instruments_dict.values()), orchestration_notes_detailed

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
