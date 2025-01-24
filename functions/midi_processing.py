import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    Uses beats instead of seconds for timing.
    """
    # Load the MIDI file as a performance object
    performance = partitura.load_performance_midi(midi_file)

    # Convert the performance into a note array
    note_array = partitura.performance.to_note_array(performance)

    # Prepare a list to hold note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Onset time in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Note velocity
            "instrument": note.get("track", "Unknown"),  # Use `track` as instrument info
        })
    
    return note_features
