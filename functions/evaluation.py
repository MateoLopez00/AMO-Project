from collections import Counter
import pretty_midi
import numpy as np

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

def pitch_class_entropy(midi_path):
    midi = pretty_midi.PrettyMIDI(midi_path)
    pitch_classes = [note.pitch % 12 for instrument in midi.instruments for note in instrument.notes]
    pitch_counts = Counter(pitch_classes)
    total_notes = sum(pitch_counts.values())
    probabilities = [count / total_notes for count in pitch_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    return entropy

def scale_consistency(midi_path, scale=[0, 2, 4, 5, 7, 9, 11]):  # Default: Major scale
    midi = pretty_midi.PrettyMIDI(midi_path)
    pitch_classes = [note.pitch % 12 for instrument in midi.instruments for note in instrument.notes]
    in_scale = sum(1 for pitch in pitch_classes if pitch in scale)
    total_notes = len(pitch_classes)
    return in_scale / total_notes if total_notes > 0 else 0.0

def average_polyphony(midi_path):
    midi = pretty_midi.PrettyMIDI(midi_path)
    times = sorted(set(note.start for instrument in midi.instruments for note in instrument.notes) |
                   set(note.end for instrument in midi.instruments for note in instrument.notes))
    polyphony = [
        sum(1 for instrument in midi.instruments for note in instrument.notes if note.start <= t < note.end)
        for t in times
    ]
    return np.mean(polyphony) if polyphony else 0.0

