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
    # prepare arrays
    new_ch = (np.full((nmat.shape[0],), new_channels) if np.ndim(new_channels)==0
              else np.array(new_channels))
    new_pr = (np.full((nmat.shape[0],), new_programs) if np.ndim(new_programs)==0
              else np.array(new_programs))
    return np.concatenate([nmat, new_ch[:,None], new_pr[:,None]], axis=1)

# --- Write raw note-matrix to MIDI ---
def write_nmat_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Turn a raw 9-column matrix into a MIDI file by using original channel as GM channel
    and default program 0 (Acoustic Grand Piano) for all notes.
    """
    # derive new_channel/program from original channel
    # original channel column is index 2 (0-based), zero-based
    # GM channels are 1-based
    channels = nmat[:,2].astype(int) + 1
    programs = np.zeros_like(channels)
    # enrich to 11 columns
    nmat_enriched = enrich_nmat(nmat, channels, programs)
    write_array_to_midi(nmat_enriched, output_filename, ticks_per_beat, tempo)

# --- Alias for roundtrip without orchestration ---
def roundtrip_nmat(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Write out a MIDI containing exactly the notes in a 9-col note matrix,
    using original channels and default piano patch.
    """
    write_nmat_to_midi(nmat, output_filename, ticks_per_beat, tempo)
