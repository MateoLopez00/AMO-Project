import pretty_midi

# Limit note range for specific instruments
def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

# Create and populate pretty_midi instruments
def create_and_assign_instruments(layer_notes, instrument_map):
    """
    Create and assign pretty_midi instruments to notes based on their layers.
    """
    import pretty_midi

    instruments = {}
    orchestration_notes = []
    for layer, (notes, name, min_pitch, max_pitch) in layer_notes.items():
        # Correct instrument name mapping
        corrected_name = "Contrabass" if name == "Double Bass" else name

        # Create pretty_midi instrument
        try:
            program = pretty_midi.instrument_name_to_program(corrected_name)
            instrument = pretty_midi.Instrument(program=program, name=corrected_name)
        except ValueError as e:
            print(f"Error with instrument name '{name}': {e}")
            continue

        # Filter notes within the instrument's range
        limited_notes = limit_range(notes, min_pitch, max_pitch)
        orchestration_notes.extend(limited_notes)
        
        for note in limited_notes:
            note['instrument'] = corrected_name
            instrument.notes.append(pretty_midi.Note(
                velocity=note['velocity'],
                pitch=note['pitch'],
                start=note['start'],
                end=note['end']
            ))
        
        instruments[layer] = instrument
    
    return instruments, orchestration_notes

