import numpy as np
from midi_processing import write_midi_full
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


def write_matrix_or_data(data, output_filename, midi_data=None, ticks_per_beat=480, tempo=500000):
    """
    Dispatch helper: if you provide a midi_data dict, performs an exact round-trip;
    if you provide a NumPy note-matrix, writes via write_array_to_midi.
    """
    # Case A: full round-trip from midi_data dict
    if isinstance(data, dict):
        write_midi_full(data, output_filename)
        return

    # Case B: NumPy array handling
    if isinstance(data, np.ndarray):
        cols = data.shape[1]
        # Raw 9-col matrix: require midi_data to round-trip
        if cols == 9:
            if midi_data is None:
                raise ValueError(
                    "Must supply midi_data dict to round-trip a raw 9-column note matrix."
                )
            write_midi_full(midi_data, output_filename)
        # Enriched >=11-col matrix: orchestrated write
        else:
            write_array_to_midi(data, output_filename, ticks_per_beat, tempo)
        return

    raise TypeError("Data must be either a midi_data dict or a NumPy array.")
