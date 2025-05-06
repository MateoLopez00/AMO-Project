import numpy as np
from midi_processing import write_midi_full, read_midi_full
from orchestration import write_array_to_midi

def nmat_to_note_list(nmat):
    """
    Converts a note matrix (assumed to have columns:
    [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec])
    into a list of dictionaries with keys "pitch" and "start".
    We use onset_sec (column index 5) as the note's start time.
    """
    note_list = []
    for row in nmat:
        start_time = row[5] if len(row) >= 7 else row[0]
        note_list.append({
            "pitch": row[3],
            "start": start_time
        })
    return note_list


def write_matrix_or_data(data, output_filename, midi_file=None, ticks_per_beat=480, tempo=500000):
    """
    Helper to write MIDI from either:
      - a full midi_data dict (exact round-trip),
      - a raw 9-column note matrix + midi_file path (round-trip),
      - an enriched >=11-column matrix (orchestrated write).

    Args:
      data: midi_data dict or NumPy note-matrix.
      output_filename: path to save the .mid file.
      midi_file: optional path to original MIDI when only raw matrix is provided.
      ticks_per_beat: MIDI PPQ (default 480).
      tempo: tempo in microseconds per beat (default 500000 = 120 BPM).
    """
    # Case 1: full-midi dict → exact round-trip
    if isinstance(data, dict):
        write_midi_full(data, output_filename)
        return

    # Case 2: NumPy note-matrix
    if isinstance(data, np.ndarray):
        cols = data.shape[1]
        # Raw 9-col → need midi_file to read full midi_data
        if cols == 9:
            if midi_file is None:
                raise ValueError(
                    "To round-trip a raw note matrix, you must supply the midi_file path."
                )
            midi_data, _ = read_midi_full(midi_file)
            write_midi_full(midi_data, output_filename)
            return
        # Enriched >=11-col → orchestrated write
        write_array_to_midi(data, output_filename, ticks_per_beat, tempo)
        return

    raise TypeError("Data must be a midi_data dict or a NumPy note-matrix.")

