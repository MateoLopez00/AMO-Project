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

# Mapping from (combo, layer) to new MIDI channel.
orchestration_channels = {
    ("combo1", "melody"): 0,
    ("combo1", "harmony"): 1,
    ("combo1", "rhythm"): 2,
    ("combo2", "melody"): 3,
    ("combo2", "harmony"): 4,
    ("combo2", "rhythm"): 5
}

def get_combo_for_beat(start, combo1_duration=16, combo2_duration=8):
    """
    Given a note's start (in beats), returns the combo ("combo1" or "combo2")
    based on a repeating cycle of combo1_duration + combo2_duration.
    """
    cycle = combo1_duration + combo2_duration
    mod = start % cycle
    return "combo1" if mod < combo1_duration else "combo2"

def apply_orchestration(note_df):
    """
    Given a DataFrame with columns:
      [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec,
       onset_quarters, duration_quarters],
    assign new MIDI channels, GM patch numbers, and an instrument name based on the note's
    pitch (to determine its layer) and the current combo (determined by its onset time).
    
    Returns the DataFrame with three new columns: 
      'new_channel', 'new_program', and 'instrument'.
    """
    new_channels = []
    new_programs = []
    new_instruments = []  # NEW: to store the instrument names
    for idx, row in note_df.iterrows():
        pitch = row['pitch']
        onset_beats = row['onset_beats']
        if pitch > 60:
            layer = "melody"
        elif 50 <= pitch <= 60:
            layer = "harmony"
        else:
            layer = "rhythm"
        combo = get_combo_for_beat(onset_beats, combo1_duration=16, combo2_duration=8)
        instrument_name, gm_patch = instrument_combos[combo][layer][0]
        new_ch = orchestration_channels[(combo, layer)]
        new_channels.append(new_ch)
        new_programs.append(gm_patch)
        new_instruments.append(instrument_name)  # Save the instrument name
    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    note_df['new_instrument'] = new_instruments  # NEW column
    return note_df


def orchestrated_nmat_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Converts an orchestrated notematrix (with original 7 columns plus new_channel and new_program)
    into a MIDI file.
    """
    spb = tempo / 1e6
    events = []
    for row in nmat:
        onset_sec = row[5]
        duration_sec = row[6]
        off_sec = onset_sec + duration_sec
        new_ch = int(row[7])
        note = int(row[3])
        velocity = int(row[4])
        prog = int(row[8])
        events.append((onset_sec, 'note_on', new_ch, note, velocity))
        events.append((off_sec, 'note_off', new_ch, note, 0))
    events.sort(key=lambda x: (x[0], 0 if x[1]=='note_off' else 1))
    
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    unique_channels = {}
    for row in nmat:
        ch = int(row[7])
        prog = int(row[8])
        if ch not in unique_channels:
            unique_channels[ch] = prog
    for ch, prog in unique_channels.items():
        track.append(mido.Message('program_change', channel=ch, program=prog, time=0))
    
    prev_time_sec = 0.0
    for event in events:
        current_time_sec = event[0]
        delta_sec = current_time_sec - prev_time_sec
        delta_ticks = int(round(delta_sec / spb * ticks_per_beat))
        if event[1] == 'note_on':
            msg = mido.Message('note_on', channel=event[2], note=event[3], velocity=event[4], time=delta_ticks)
        else:
            msg = mido.Message('note_off', channel=event[2], note=event[3], velocity=0, time=delta_ticks)
        track.append(msg)
        prev_time_sec = current_time_sec
    mid.save(output_filename)
    print(f"Saved orchestrated MIDI to {output_filename}")
