import numpy as np
from midi_processing import read_midi_full, write_midi_full
from orchestration import write_array_to_midi

def write_matrix_or_data(data, output_filename, midi_file=None, ticks_per_beat=480, tempo=500000):
    """
    Dispatch helper: write MIDI from either:
      - a full midi_data dict (exact round-trip),
      - a raw 9-column note matrix + midi_file path (exact round-trip),
      - an enriched >=11-column matrix (orchestrated or custom write).

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
        # Raw 9-col → exact round-trip from original file
        if cols == 9:
            if midi_file is None:
                raise ValueError(
                    "To round-trip a raw note matrix, you must supply the midi_file path."
                )
            midi_data, _ = read_midi_full(midi_file)
            write_midi_full(midi_data, output_filename)
            return
        # Enriched >=11-col → write via array→MIDI (drops original metadata)
        write_array_to_midi(data, output_filename, ticks_per_beat, tempo)
        return

    raise TypeError("Data must be a midi_data dict or a NumPy note-matrix.")


def extract_note_matrix(midi_file):
    """
    Load a MIDI file and return only its 9-column note matrix as a NumPy array.
    """
    _, nmat = read_midi_full(midi_file)
    return nmat


def enrich_nmat(nmat, new_channels, new_programs):
    """
    Given a raw 9-column note matrix, append two columns:
      - new_channels (int array or scalar)
      - new_programs (int array or scalar)
    Returns an (N x 11) NumPy array ready for write_array_to_midi.
    """
    # ensure array form
    new_ch = np.full((nmat.shape[0],), new_channels) if np.ndim(new_channels) == 0 else np.array(new_channels)
    new_pr = np.full((nmat.shape[0],), new_programs) if np.ndim(new_programs) == 0 else np.array(new_programs)
    return np.concatenate([nmat, new_ch[:, None], new_pr[:, None]], axis=1)


def roundtrip_nmat(nmat, midi_file, output_filename):
    """
    Round-trip a raw 9-column note matrix back to a MIDI file by re-reading the original file's metadata.
    """
    midi_data, _ = read_midi_full(midi_file)
    write_midi_full(midi_data, output_filename)
