import pretty_midi
import numpy as np

def midi_to_nmat(file_path):
    midi_data = pretty_midi.PrettyMIDI(file_path)
    nmat = []
    beats = midi_data.get_beats()
    seconds_per_beat = beats[1] - beats[0] if len(beats) > 1 else 0.5

    for instrument in midi_data.instruments:
        for note in instrument.notes:
            onset_sec = note.start
            duration_sec = note.end - note.start
            onset_beat = onset_sec / seconds_per_beat if seconds_per_beat > 0 else 0
            duration_beat = duration_sec / seconds_per_beat if seconds_per_beat > 0 else 0
            nmat.append([
                round(onset_beat, 4),
                round(duration_beat, 4),
                instrument.program,
                note.pitch,
                note.velocity,
                round(onset_sec, 4),
                round(duration_sec, 4)
            ])
    return np.array(nmat)