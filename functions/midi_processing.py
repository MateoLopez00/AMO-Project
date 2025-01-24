import partitura

def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, using the partitura library.
    Args:
        midi_file (str): Path to the MIDI file.
    Returns:
        List[Dict]: A list of dictionaries containing note features with beats.
    """
    # Load the MIDI file as a Score object
    scores = partitura.load_score_midi(midi_file)

    # Prepare a list to hold note features
    note_features = []

    # Loop through the parts (instruments) in the score
    for part in scores.parts:
        for note in part.notes:
            note_features.append({
                "pitch": note.pitch,  # MIDI pitch
                "start": note.start.t,  # Start time in beats
                "end": note.start.t + note.duration.t,  # End time in beats
                "velocity": note.velocity,  # Note velocity
                "instrument": part.id,  # Part name or instrument info
            })

    return note_features
