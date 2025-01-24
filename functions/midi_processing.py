import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, using beats for timing
    instead of seconds, with partitura.
    """
    # Load the MIDI file as a Partitura performance
    performance = partitura.performance.Performance.from_midi(midi_file)
    
    # Get a structured array of notes from the performance
    notes = performance.note_array()

    # Prepare a list of dictionaries to hold note features
    note_features = []
    for note in notes:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Start time in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Velocity of the note
            "instrument": note.get("part", "Unknown")  # Part name as instrument info
        })
    
    return note_features
