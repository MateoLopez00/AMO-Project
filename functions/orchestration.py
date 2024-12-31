import pretty_midi

# Limit note range for specific instruments
def limit_range(notes, min_pitch, max_pitch):
    return [note for note in notes if min_pitch <= note['pitch'] <= max_pitch]

# Create and populate pretty_midi instruments
def create_and_assign_instruments(layer_notes, instrument_map):
    instruments = {}
    orchestration_notes = []
    for layer, (notes, name, min_pitch, max_pitch) in layer_notes.items():
        instrument = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(name), name=name)
        limited_notes = limit_range(notes, min_pitch, max_pitch)
        orchestration_notes.extend(limited_notes)
        for note in limited_notes:
            note['instrument'] = name
            instrument.notes.append(pretty_midi.Note(
                velocity=note['velocity'],
                pitch=note['pitch'],
                start=note['start'],
                end=note['end']
            ))
        instruments[layer] = instrument
    return instruments, orchestration_notes
