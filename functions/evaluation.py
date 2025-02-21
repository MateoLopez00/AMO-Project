from collections import Counter
import pretty_midi
import numpy as np

# Evaluate the orchestration
def evaluate_orchestration(piano_notes, orchestration_notes, instrument_combos, combo1_duration=16, combo2_duration=8):
    # Nested function for pitch coverage
    def evaluate_pitch_coverage():
        piano_pitches = set(note["pitch"] for note in piano_notes)
        orchestration_pitches = set(note["pitch"] for note in orchestration_notes)
        return len(piano_pitches & orchestration_pitches) / len(piano_pitches) if len(piano_notes) > 0 else 0

    # Nested function for timing accuracy
    def evaluate_timing_accuracy(tolerance=0.1):
        matches = sum(
            any(abs(p["start"] - o["start"]) <= tolerance and p["pitch"] == o["pitch"]
                for o in orchestration_notes)
            for p in piano_notes
        )
        return matches / len(piano_notes) if len(piano_notes) > 0 else 0

    # New nested function for range appropriateness.
    # For each note, we:
    #   1. Determine its layer (melody, harmony, or rhythm) based on its pitch.
    #   2. Determine the current combo (using get_combo_for_beat on note['start']).
    #   3. Get the candidate instruments (with their ranges) for that layer.
    #   4. Check if the note's pitch falls within at least one candidate's range.
    # Then, we compute the fraction of notes that are in range.
    def evaluate_range_appropriateness():
        def get_layer(p):
            if p > 60:
                return "melody"
            elif 50 <= p <= 60:
                return "harmony"
            else:
                return "rhythm"
        out_of_range = 0
        total = 0
        for note in orchestration_notes:
            total += 1
            layer = get_layer(note['pitch'])
            combo_id = get_combo_for_beat(note['start'], combo1_duration, combo2_duration)
            candidate_instruments = instrument_combos[combo_id][layer]
            # Check if note's pitch falls within at least one candidate instrument's range.
            in_range = any(min_pitch <= note['pitch'] <= max_pitch for (inst_name, min_pitch, max_pitch) in candidate_instruments)
            if not in_range:
                out_of_range += 1
        return 1 - (out_of_range / total) if total > 0 else 0

    return {
        "Pitch Coverage": evaluate_pitch_coverage(),
        "Timing Accuracy": evaluate_timing_accuracy(),
        "Range Appropriateness": evaluate_range_appropriateness(),
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

