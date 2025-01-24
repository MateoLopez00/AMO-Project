import partitura

def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file using beats as the timing unit.
    Args:
        midi_file (str): Path to the MIDI file.
    Returns:
        List[Dict]: A list of dictionaries containing note features.
    """
    # Load the MIDI file as a Score object
    score = partitura.load_score_midi(midi_file)

    # Extract note array from the score
    note_array = partitura.utils.ensure_notearray(score)

    # Prepare a list of dictionaries for note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Onset in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Note velocity
            "instrument": note.get("id_in_part", "Unknown")  # Use `id_in_part` for instrument info
        })
    
    return note_features
