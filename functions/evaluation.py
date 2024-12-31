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
