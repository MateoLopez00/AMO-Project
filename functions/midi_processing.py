import partitura

# Load and process MIDI files
def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file, ensuring instruments are properly named.
    Uses beats instead of seconds for timing.
    """
    score = partitura.load_score_midi(midi_file)
    notes = []
    for note in score.notes:
        notes.append({
            "pitch": note.pitch,
            "start": note.start.t / score.quarter_note_duration,  # Convert time to beats
            "end": note.end.t / score.quarter_note_duration,      # Convert time to beats
            "velocity": note.velocity,
            "instrument": note.voice if hasattr(note, "voice") else "Unknown"
        })
    return notes
