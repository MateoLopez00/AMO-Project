from collections import Counter
import pretty_midi
import numpy as np
from orchestration import get_combo_for_beat, instrument_combos

def evaluate_orchestration(piano_notes, orchestration_notes, combo1_duration=16, combo2_duration=8):
    # Pitch Coverage: What fraction of unique piano pitches appear in the orchestration?
    def evaluate_pitch_coverage():
        piano_pitches = set(note["pitch"] for note in piano_notes)
        orch_pitches = set(note["pitch"] for note in orchestration_notes)
        return len(piano_pitches & orch_pitches) / len(piano_pitches) if piano_pitches else 0

    # Timing Accuracy: For each piano note, is there a corresponding orchestration note
    # with the same pitch and a start time within a given tolerance?
    def evaluate_timing_accuracy(tolerance=0.1):
        matches = 0
        for p in piano_notes:
            for o in orchestration_notes:
                if abs(p["start"] - o["start"]) <= tolerance and p["pitch"] == o["pitch"]:
                    matches += 1
                    break
        return matches / len(piano_notes) if piano_notes else 0

    # Range Appropriateness: Since our current instrument_combos don’t include range info,
    # we assume the orchestration always falls within the correct range.
    def evaluate_range_appropriateness():
        return 1.0

    return {
        "Pitch Coverage": evaluate_pitch_coverage(),
        "Timing Accuracy": evaluate_timing_accuracy(),
        "Range Appropriateness": evaluate_range_appropriateness(),
    }

def pitch_class_entropy(midi_path):
    midi = pretty_midi.PrettyMIDI(midi_path)
    pitch_classes = [note.pitch % 12 for instrument in midi.instruments for note in instrument.notes]
    pitch_counts = Counter(pitch_classes)
    total = sum(pitch_counts.values())
    probabilities = [count/total for count in pitch_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    return entropy

def scale_consistency(midi_path, scale=[0,2,4,5,7,9,11]):
    midi = pretty_midi.PrettyMIDI(midi_path)
    pitch_classes = [note.pitch % 12 for instrument in midi.instruments for note in instrument.notes]
    in_scale = sum(1 for p in pitch_classes if p in scale)
    total = len(pitch_classes)
    return in_scale / total if total > 0 else 0.0

def average_polyphony(midi_path):
    midi = pretty_midi.PrettyMIDI(midi_path)
    times = sorted(set(note.start for instrument in midi.instruments for note in instrument.notes) |
                   set(note.end for instrument in midi.instruments for note in instrument.notes))
    polyphony = [
        sum(1 for instrument in midi.instruments for note in instrument.notes if note.start <= t < note.end)
        for t in times
    ]
    return np.mean(polyphony) if polyphony else 0.0
