import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    Uses beats instead of seconds for timing.
    """
    # Load the MIDI file as a partitura Score
    scores = partitura.load_score_midi(midi_file)
    
    # Extract note array from the score
    note_array = partitura.utils.get_note_array(scores)
    
    # Prepare a list to hold note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Onset in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Note velocity
            "instrument": note.get("id_in_part", "Unknown"),  # Use `id_in_part` as instrument info
        })
    
    return note_features
