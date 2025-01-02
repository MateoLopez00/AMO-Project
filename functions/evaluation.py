# Evaluate the orchestration
def evaluate_orchestration(piano_notes, orchestration_notes, instrument_ranges):
    """
    Evaluate the orchestration using pitch coverage, timing accuracy, and range appropriateness.
    """
    def evaluate_pitch_coverage():
        piano_pitches = set(note['pitch'] for note in piano_notes)
        orchestration_pitches = set(note['pitch'] for note in orchestration_notes)
        return len(piano_pitches & orchestration_pitches) / len(piano_pitches)

    def evaluate_timing_accuracy(tolerance=0.1):
        matches = sum(
            any(abs(p['start'] - o['start']) <= tolerance and p['pitch'] == o['pitch']
                for o in orchestration_notes)
            for p in piano_notes
        )
        return matches / len(piano_notes)

    def evaluate_range_appropriateness():
        out_of_range = sum(
            not (instrument_ranges.get(note['instrument'], (0, 127))[0] <= note['pitch'] <=
                 instrument_ranges.get(note['instrument'], (0, 127))[1])
            for note in orchestration_notes
        )
        return 1 - out_of_range / len(orchestration_notes)

    return {
        "Pitch Coverage": evaluate_pitch_coverage(),
        "Timing Accuracy": evaluate_timing_accuracy(),
        "Range Appropriateness": evaluate_range_appropriateness()
    }

def evaluate_midi(predicted_midi_path, ground_truth_midi_path, tolerance=0.1):
    """
    Evaluate the precision, recall, and F1-score between a predicted MIDI file and ground truth.

    Args:
        predicted_midi_path (str): Path to the predicted orchestration MIDI file.
        ground_truth_midi_path (str): Path to the ground truth orchestration MIDI file.
        tolerance (float): Timing tolerance for matching notes (in seconds).

    Returns:
        dict: Precision, recall, and F1-score.
    """
    import pretty_midi

    # Load MIDI files
    predicted_midi = pretty_midi.PrettyMIDI(predicted_midi_path)
    ground_truth_midi = pretty_midi.PrettyMIDI(ground_truth_midi_path)

    # Extract notes as (pitch, start_time) pairs
    def extract_note_tokens(midi):
        tokens = []
        for instrument in midi.instruments:
            for note in instrument.notes:
                tokens.append((note.pitch, round(note.start, 4)))  # Round start time for tolerance
        return set(tokens)

    predicted_tokens = extract_note_tokens(predicted_midi)
    ground_truth_tokens = extract_note_tokens(ground_truth_midi)

    # Calculate TP, FP, FN
    tp = len(predicted_tokens & ground_truth_tokens)
    fp = len(predicted_tokens - ground_truth_tokens)
    fn = len(ground_truth_tokens - predicted_tokens)

    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1_score
    }

