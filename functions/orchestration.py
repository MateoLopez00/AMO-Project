# orchestration.py
import pandas as pd
import numpy as np
import mido

# Define instrument combinations and mapping of (combo, layer) to new MIDI channel.
instrument_combos = {
    "combo1": {  # Strings combo
        "melody": [("Violin", 55, 103), ("Viola", 48, 91)],
        "harmony": [("Cello", 36, 76)],
        "rhythm": [("Acoustic Bass", 28, 67), ("Tuba", 18, 55)]
    },
    "combo2": {  # Winds combo
        "melody": [("Flute", 60, 96), ("Oboe", 58, 91)],
        "harmony": [("Clarinet", 50, 94), ("Bassoon", 34, 75)],
        "rhythm": [("French Horn", 34, 77), ("Trumpet", 55, 82), ("Tuba", 18, 55)]
    }
}

orchestration_channels = {
    ("combo1", "melody"): 0,
    ("combo1", "harmony"): 1,
    ("combo1", "rhythm"): 2,
    ("combo2", "melody"): 3,
    ("combo2", "harmony"): 4,
    ("combo2", "rhythm"): 5
}

def apply_orchestration(note_df):
    """
    Takes a DataFrame (with columns: onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec)
    and assigns new MIDI channels and instrument program numbers based on note pitch and the note’s onset.
    Returns the updated DataFrame with two additional columns: 'new_channel' and 'new_program'.
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
        # Alternate instrument combos every 8 beats.
        combo = "combo1" if (int(onset_beats // 8) % 2 == 0) else "combo2"
        # Select the first instrument in the list for that layer (could be extended to more complex selection)
        instrument = instrument_combos[combo][layer][0]
        program = instrument[1]  # Use the lower bound program number
        new_channel = orchestration_channels[(combo, layer)]
        new_channels.append(new_channel)
        new_programs.append(program)
    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    return note_df

def orchestrated_nmat_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Converts an orchestrated notematrix (which must have 9 columns: the original 7 plus new_channel and new_program)
    into a new MIDI file.
    
    It creates a single track MIDI file that inserts note_on/note_off messages using the new channels.
    Program change messages are inserted at time 0 for each new channel.
    """
    spb = tempo / 1e6  # seconds per beat
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
    
    # Insert a tempo meta message
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Insert program_change messages for each new channel (only once per channel)
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
