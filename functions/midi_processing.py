import pretty_midi

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    """
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    notes = []
    for instrument in midi_data.instruments:
        instrument_name = instrument.name if instrument.name else "Unknown"
        for note in instrument.notes:
            notes.append({
                "pitch": note.pitch,
                "start": note.start,
                "end": note.end,
                "velocity": note.velocity,
                "instrument": instrument_name
            })
    return notes
