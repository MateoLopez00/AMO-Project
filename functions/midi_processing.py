import partitura

def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file using partitura and ensure_notearray.
    Args:
        midi_file (str): Path to the MIDI file.
    Returns:
        List[Dict]: A list of dictionaries with note features (timing in beats).
    """
    # Load the MIDI file as a Score object
    score = partitura.load_score_midi(midi_file)

    # Convert the score to a note array
    note_array = partitura.utils.ensure_notearray(score)

    # Prepare a list of dictionaries with note features
    note_features = []
    for note in note_array:
        note_features.append({
            "pitch": note["pitch"],  # MIDI pitch
            "start": note["onset_beat"],  # Onset in beats
            "end": note["onset_beat"] + note["duration_beat"],  # End time in beats
            "velocity": note["velocity"],  # Velocity
            "instrument": note["id_in_part"],  # Instrument or part ID
        })

    return note_features
