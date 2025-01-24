import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file using partitura,
    with all timing information converted to beats.
    """
    # Load the MIDI file as a performance object
    performance = partitura.performance.load_performance_midi(midi_file)
    
    # Extract notes as a structured array
    note_array = performance.note_array()

    # Prepare a list of dictionaries with note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Start time in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # MIDI velocity
            "instrument": note.get("track", "Unknown"),  # Track info as instrument proxy
        })
    
    return note_features
