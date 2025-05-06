import numpy as np
from midi_processing import read_midi_full
from orchestration import write_array_to_midi

# --- Note matrix extraction ---
def extract_note_matrix(midi_file):
    """
    Load a MIDI file and return its raw 9-column note matrix.
    """
    _, nmat = read_midi_full(midi_file)
    return nmat

# --- Enrich matrix with new columns ---
def enrich_nmat(nmat, new_channels, new_programs):
    """
    Given a raw 9-column note matrix, append two columns:
      - new_channels (int or array)
      - new_programs (int or array)
    Returns an (N x 11) NumPy array for write_array_to_midi.
    """
    new_ch = (np.full(nmat.shape[0], new_channels) if np.ndim(new_channels)==0 else np.array(new_channels))
    new_pr = (np.full(nmat.shape[0], new_programs) if np.ndim(new_programs)==0 else np.array(new_programs))
    return np.concatenate([nmat, new_ch[:, None], new_pr[:, None]], axis=1)

# --- Write raw note-matrix to MIDI preserving metadata ---
def roundtrip_nmat(nmat, midi_file, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Write a MIDI containing exactly the notes in a 9-col note matrix,
    preserving metadata from the original MIDI file.

    Args:
      nmat: N×9 array of notes
      midi_file: path to original .mid for metadata
      output_filename: where to save the new .mid
      ticks_per_beat, tempo: optional defaults
    """
    # Delegate to write_array_to_midi with metadata copy
    write_array_to_midi(
        nmat, output_filename,
        midi_file=midi_file,
        ticks_per_beat=ticks_per_beat,
        tempo=tempo
    )
