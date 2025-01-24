import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    Uses beats instead of seconds for timing.
    """
    # Load the MIDI file as a partitura Score
    score = partitura.load_score_midi(midi_file)
    
    # Extract notes from the score
    notes = partitura.utils.get_notes(score)
    
    # Prepare a list to hold note features
    note_features = []
    for note in notes:
        note_features.append({
            "pitch": note["pitch"],
            "start": note["onset_beat"],  # Use beats instead of seconds
            "end": note["onset_beat"] + note["duration_beat"],  # Calculate end in beats
            "velocity": note["velocity"],
            "instrument": note.get("voice", "Unknown"),  # Use voice if available
        })
    
    return note_features
