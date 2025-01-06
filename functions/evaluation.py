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

def evaluate_instrument_agnostic_metrics(ground_truth_midi_path, predicted_midi_path, tolerance=0.1):
    import pretty_midi

    def extract_notes(midi):
        notes = []
        for instrument in midi.instruments:
            for note in instrument.notes:
                notes.append((note.pitch, note.start))
        return set(notes)

    ground_truth = pretty_midi.PrettyMIDI(ground_truth_midi_path)
    predicted = pretty_midi.PrettyMIDI(predicted_midi_path)

    ground_truth_notes = extract_notes(ground_truth)
    predicted_notes = extract_notes(predicted)

    matched = ground_truth_notes & predicted_notes
    true_positives = len(matched)
    false_positives = len(predicted_notes - ground_truth_notes)
    false_negatives = len(ground_truth_notes - predicted_notes)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"Precision": precision, "Recall": recall, "F1-Score": f1_score}
