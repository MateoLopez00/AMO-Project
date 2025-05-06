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

# Mapping from (combo, layer) to true GM channel numbers (1-16).
orchestration_channels = {
    ("combo1", "melody"): 1,
    ("combo1", "harmony"): 2,
    ("combo1", "rhythm"): 3,
    ("combo2", "melody"): 4,
    ("combo2", "harmony"): 5,
    ("combo2", "rhythm"): 6
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
    Assigns new MIDI channels (1-16), GM patch numbers, and instrument names
    to each note based on its pitch and beat position.
    Adds three new columns: 'new_channel', 'new_program', 'new_instrument'.
    """
    new_channels = []
    new_programs = []
    new_instruments = []

    for _, row in note_df.iterrows():
        pitch = row['pitch']
        onset_beats = row['onset_beats']

        # Determine layer by pitch
        if pitch > 60:
            layer = "melody"
        elif 50 <= pitch <= 60:
            layer = "harmony"
        else:
            layer = "rhythm"

        # Determine which combo applies for this note
        combo = get_combo_for_beat(onset_beats)

        # Lookup GM channel and program
        gm_channel = orchestration_channels[(combo, layer)]
        instrument_name, gm_patch = instrument_combos[combo][layer][0]

        new_channels.append(gm_channel)
        new_programs.append(gm_patch)
        new_instruments.append(instrument_name)

    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    note_df['new_instrument'] = new_instruments
    return note_df


def orchestrated_nmat_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Converts an orchestrated notematrix (with 9 original + 3 new columns) into a MIDI file.
    Expects 'new_channel' in column index 9 (1-16) and 'new_program' in index 10.
    """
    spb = tempo / 1e6
    events = []

    # Build note_on/note_off events list
    for row in nmat:
        onset_sec = row[5]
        duration_sec = row[6]
        off_sec = onset_sec + duration_sec
        gm_channel = int(row[9])     # 1-16
        note = int(row[3])
        velocity = int(row[4])

        # Mido channels are 0-based, so subtract 1
        ch = gm_channel - 1
        events.append((onset_sec, 'note_on', ch, note, velocity))
        events.append((off_sec, 'note_off', ch, note, 0))

    # Sort by time (and note_off before note_on at same time)
    events.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))

    # Create MIDI file and track
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # Program changes for each used channel
    unique_channels = {}
    for row in nmat:
        gm_channel = int(row[9])
        prog = int(row[10])
        ch = gm_channel - 1
        if ch not in unique_channels:
            unique_channels[ch] = prog

    for ch, prog in unique_channels.items():
        track.append(mido.Message('program_change', channel=ch, program=prog, time=0))

    # Write all note events with proper delta times
    prev_time_sec = 0.0
    for t_sec, kind, ch, note, vel in events:
        delta_sec = t_sec - prev_time_sec
        delta_ticks = int(round(delta_sec / spb * ticks_per_beat))
        if kind == 'note_on':
            msg = mido.Message('note_on', channel=ch, note=note, velocity=vel, time=delta_ticks)
        else:
            msg = mido.Message('note_off', channel=ch, note=note, velocity=0, time=delta_ticks)
        track.append(msg)
        prev_time_sec = t_sec

    mid.save(output_filename)
    print(f"Saved orchestrated MIDI to {output_filename}")


def write_array_to_midi(nmat, output_filename, ticks_per_beat=480, tempo=500000):
    """
    Converts a note matrix array back into a MIDI file.
    This is a convenience wrapper around orchestrated_nmat_to_midi.
    """
    orchestrated_nmat_to_midi(nmat, output_filename, ticks_per_beat, tempo)
