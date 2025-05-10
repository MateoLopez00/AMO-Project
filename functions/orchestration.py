import mido
import pandas as pd
import numpy as np

# Instrument combos using GM patch numbers.
instrument_combos = {
    "combo1": {  # Strings combo
        "melody": [("Violin", 40), ("Viola", 41)],
        "harmony": [("Cello", 42)],
        "rhythm": [("Acoustic Bass", 32), ("Tuba", 58)]
    },
    "combo2": {  # Winds combo
        "melody": [("Flute", 73), ("Oboe", 68)],
        "harmony": [("Clarinet", 71), ("Bassoon", 70)],
        "rhythm": [("French Horn", 60), ("Trumpet", 56), ("Tuba", 58)]
    }
}

# Mapping from (combo, layer) to GM channel numbers (1-16)
orchestration_channels = {
    ("combo1", "melody"): 1,
    ("combo1", "harmony"): 2,
    ("combo1", "rhythm"): 3,
    ("combo2", "melody"): 4,
    ("combo2", "harmony"): 5,
    ("combo2", "rhythm"): 6
}

# Function to cycle combos every 8 beats
combo1_duration = 8
combo2_duration = 8

def get_combo_for_beat(onset_beats):
    """
    Returns 'combo1' or 'combo2' based on an 8-beat cycle.
    """
    cycle = combo1_duration + combo2_duration
    return "combo1" if (onset_beats % cycle) < combo1_duration else "combo2"


def apply_orchestration(note_df):
    """
    Assign each note to a combo (combo1 or combo2) based on its onset in beats,
    then pick an instrument from that combo and assign channel and program.
    Balances melody/harmony/rhythm layers using pitch thresholds.
    Adds new_channel, new_program, new_instrument.
    """
    new_channels = []
    new_programs = []
    new_instruments = []

    for _, row in note_df.iterrows():
        pitch = row['pitch']
        onset = row['onset_beats']

        # Determine layer by pitch
        if pitch > 60:
            layer = 'melody'
        elif pitch >= 50:
            layer = 'harmony'
        else:
            layer = 'rhythm'

        # Choose combo based on onset beat
        combo = get_combo_for_beat(onset)

        # Pick the first instrument in the layer list
        instr_name, gm_patch = instrument_combos[combo][layer][0]
        gm_channel = orchestration_channels[(combo, layer)]

        new_channels.append(gm_channel)
        new_programs.append(gm_patch)
        new_instruments.append(instr_name)

    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    note_df['new_instrument'] = new_instruments
    return note_df

# The MIDI-writing functions remain unchanged below

def orchestrated_nmat_to_midi(nmat, output_filename, midi_file=None,
                               ticks_per_beat=480, tempo=500000):
    # ... existing code ...
    pass

def write_array_to_midi(nmat, output_filename, midi_file=None,
                        ticks_per_beat=480, tempo=500000):
    """Wrapper for orchestrated_nmat_to_midi"""
    orchestrated_nmat_to_midi(nmat, output_filename,
                               midi_file=midi_file,
                               ticks_per_beat=ticks_per_beat,
                               tempo=tempo)
