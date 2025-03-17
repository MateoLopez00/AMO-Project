import mido
import pandas as pd
import numpy as np

###############################################################################
# 1. Define Instrument Combos (with GM patch numbers)
###############################################################################
instrument_combos = {
    "combo1": {  # Strings combo
        "melody": [
            ("Violin", 40),   # GM #40
            ("Viola", 41)    # GM #41
        ],
        "harmony": [
            ("Cello", 42)    # GM #42
        ],
        "rhythm": [
            ("Acoustic Bass", 32),  # GM #32
            ("Tuba", 58)           # GM #58
        ]
    },
    "combo2": {  # Winds combo
        "melody": [
            ("Flute", 73),   # GM #73
            ("Oboe", 68)     # GM #68
        ],
        "harmony": [
            ("Clarinet", 71),  # GM #71
            ("Bassoon", 70)    # GM #70
        ],
        "rhythm": [
            ("French Horn", 60),  # GM #60
            ("Trumpet", 56),      # GM #56
            ("Tuba", 58)          # GM #58
        ]
    }
}

###############################################################################
# 2. Define a mapping from (combo, layer) to new MIDI channels
###############################################################################
orchestration_channels = {
    ("combo1", "melody"): 0,
    ("combo1", "harmony"): 1,
    ("combo1", "rhythm"): 2,
    ("combo2", "melody"): 3,
    ("combo2", "harmony"): 4,
    ("combo2", "rhythm"): 5
}

###############################################################################
# 3. Orchestration Logic: Segment into layers and assign channels/programs
###############################################################################
def apply_orchestration(note_df):
    """
    Takes a DataFrame (columns: onset_beats, duration_beats, channel, pitch, velocity, 
    onset_sec, duration_sec) and assigns new MIDI channels and GM patch numbers based 
    on pitch (melody/harmony/rhythm) and time (alternating combos every 8 beats).
    Returns the updated DataFrame with 'new_channel' and 'new_program' columns added.
    """
    new_channels = []
    new_programs = []

    for idx, row in note_df.iterrows():
        pitch = row['pitch']
        onset_beats = row['onset_beats']

        # Segment by pitch
        if pitch > 60:
            layer = "melody"
        elif 50 <= pitch <= 60:
            layer = "harmony"
        else:
            layer = "rhythm"

        # Alternate combos every 8 beats
        combo = "combo1" if (int(onset_beats // 8) % 2 == 0) else "combo2"

        # Choose the first instrument in the combo's layer list
        instrument_name, gm_patch = instrument_combos[combo][layer][0]

        # Map combo+layer to a new MIDI channel
        new_ch = orchestration_channels[(combo, layer)]

        new_channels.append(new_ch)
        new_programs.append(gm_patch)

    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    return note_df

###############################################################################
# 4. Write the orchestrated note matrix to a MIDI file
###############################################################################
def orchestrated_nmat_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Converts an orchestrated notematrix (with 9 columns: the original 7 plus new_channel, new_program)
    into a MIDI file. 
    """
    spb = tempo / 1e6  # seconds per beat
    events = []

    # Build a list of note_on / note_off events
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

    # Sort events by time, ensuring note_off is before note_on if simultaneous
    events.sort(key=lambda x: (x[0], 0 if x[1]=='note_off' else 1))

    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Insert tempo meta message
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # Insert program_change messages at time=0 for each new channel
    unique_channels = {}
    for row in nmat:
        ch = int(row[7])
        prog = int(row[8])
        if ch not in unique_channels:
            unique_channels[ch] = prog

    for ch, prog in unique_channels.items():
        track.append(mido.Message('program_change', channel=ch, program=prog, time=0))

    # Convert each event into a MIDI message
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
