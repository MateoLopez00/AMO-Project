import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    Uses beats instead of seconds for timing.
    """
    # Load the MIDI file as a performance object
    performance = partitura.load_performance_midi(midi_file)
    
    # Extract notes as an array
    note_array = partitura.utils.note_array_from_performance(performance)

    # Prepare a list to hold note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Onset time in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Note velocity
            "instrument": note.get("track", "Unknown"),  # Track info as instrument proxy
        })

    return note_features
