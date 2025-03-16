# orchestration.py

# Define instrument combos
instrument_combos = {
    "combo1": {  # Strings combo
        "melody": [
            ("Violin", 55, 103),
            ("Viola", 48, 91)
        ],
        "harmony": [
            ("Cello", 36, 76)
        ],
        "rhythm": [
            ("Acoustic Bass", 28, 67),
            ("Tuba", 18, 55)
        ],
    },
    "combo2": {  # Winds combo
        "melody": [
            ("Flute", 60, 96),
            ("Oboe", 58, 91)
        ],
        "harmony": [
            ("Clarinet", 50, 94),
            ("Bassoon", 34, 75)
        ],
        "rhythm": [
            ("French Horn", 34, 77),
            ("Trumpet", 55, 82),
            ("Tuba", 18, 55)
        ],
    }
}

# Mapping from (combo, layer) to new MIDI channel
orchestration_channels = {
    ("combo1", "melody"): 0,
    ("combo1", "harmony"): 1,
    ("combo1", "rhythm"): 2,
    ("combo2", "melody"): 3,
    ("combo2", "harmony"): 4,
    ("combo2", "rhythm"): 5,
}

def apply_orchestration(note_df):
    """
    For each note in the DataFrame, determine its layer (melody/harmony/rhythm) based on pitch,
    choose an instrument combo based on its onset (alternating every 8 beats), and assign:
      - new_channel (from orchestration_channels)
      - new_program (the chosen instrument’s program number, here the lower bound)
    Adds columns 'new_channel' and 'new_program' to the DataFrame.
    """
    new_channels = []
    new_programs = []
    for idx, row in note_df.iterrows():
        pitch = row['pitch']
        onset_beats = row['onset_beats']
        if pitch > 60:
            layer = "melody"
        elif 50 <= pitch <= 60:
            layer = "harmony"
        else:
            layer = "rhythm"
        combo = "combo1" if (int(onset_beats // 8) % 2 == 0) else "combo2"
        instrument_list = instrument_combos[combo][layer]
        selected_instrument = instrument_list[0]  # select the first instrument for simplicity
        program_num = selected_instrument[1]
        new_ch = orchestration_channels[(combo, layer)]
        new_channels.append(new_ch)
        new_programs.append(program_num)
    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    return note_df
