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
    Determine which combo applies for a given start beat.
    """
    cycle = combo1_duration + combo2_duration
    return "combo1" if (start % cycle) < combo1_duration else "combo2"

def apply_orchestration(note_df):
    """
    Add 'new_channel', 'new_program', 'new_instrument' to each note row.
    """
    new_channels = []
    new_programs = []
    new_instruments = []

    for _, row in note_df.iterrows():
        pitch = row['pitch']
        onset = row['onset_beats']
        # layer
        if pitch > 60:
            layer = 'melody'
        elif pitch >= 50:
            layer = 'harmony'
        else:
            layer = 'rhythm'
        combo = get_combo_for_beat(onset)
        gm_ch = orchestration_channels[(combo, layer)]
        instr_name, gm_patch = instrument_combos[combo][layer][0]
        new_channels.append(gm_ch)
        new_programs.append(gm_patch)
        new_instruments.append(instr_name)

    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    note_df['new_instrument'] = new_instruments
    return note_df

def orchestrated_nmat_to_midi(nmat, output_filename, midi_file=None,
                               ticks_per_beat=480, tempo=500000):
    """
    Build a new MIDI file from a note-matrix, preserving metadata if provided.
    Supports raw (9-col) or enriched (>=11-col) matrices:
      - 9 columns: auto-enrich with original channel and piano patch
      - >=11 columns: use provided new_channel/new_program columns
    """
    # Enrich raw 9-col matrix
    ncols = nmat.shape[1]
    if ncols == 9:
        ch = nmat[:, 2].astype(int) + 1
        pr = np.zeros_like(ch)
        nmat = np.concatenate([nmat, ch[:, None], pr[:, None]], axis=1)

    # Create MIDI file and primary track
    if midi_file:
        orig = mido.MidiFile(midi_file)
        mid = mido.MidiFile(type=orig.type,
                            ticks_per_beat=orig.ticks_per_beat)
        track = mido.MidiTrack(); mid.tracks.append(track)
        # Copy meta messages (tempo, time/key signature) but skip end_of_track
        for msg in orig.tracks[0]:
            if msg.is_meta and msg.type != 'end_of_track':
                track.append(msg.copy(time=msg.time))
    else:
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack(); mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # === Updated block: Build note events in ticks ===
    # Use onset_quarters (col 7) and duration_quarters (col 8) to compute ticks
    events = []  # (abs_tick, is_off, channel, pitch, velocity)
    for row in nmat:
        onset_q  = row[7]
        dur_q    = row[8]
        onset_tick = int(round(onset_q * mid.ticks_per_beat))
        dur_ticks  = int(round(dur_q * mid.ticks_per_beat))
        off_tick   = onset_tick + dur_ticks

        ch   = int(row[9]) - 1    # new_channel col 9 → zero-based
        note = int(row[3])
        vel  = int(row[4])
        # note_on = False priority, note_off = True
        events.append((onset_tick, False, ch, note, vel))
        events.append((off_tick,   True,  ch, note, 0))

    # Sort by tick, with note_off before note_on when tied
    events.sort(key=lambda e: (e[0], e[1]))

    # Program changes
    used = {}
    for row in nmat:
        ch = int(row[9]) - 1
        pr = int(row[10])
        if ch not in used:
            used[ch] = pr
    for ch, pr in used.items():
        track.append(mido.Message('program_change',
                                  channel=ch, program=pr, time=0))

    # Write note events with delta ticks
    last_tick = 0
    for abs_tick, is_off, ch, note, vel in events:
        delta = abs_tick - last_tick
        if not is_off:
            msg = mido.Message('note_on',  channel=ch,
                                note=note, velocity=vel, time=delta)
        else:
            msg = mido.Message('note_off', channel=ch,
                                note=note, velocity=0,   time=delta)
        track.append(msg)
        last_tick = abs_tick

    # Final end_of_track
    track.append(mido.MetaMessage('end_of_track', time=0))
    mid.save(output_filename)

def write_array_to_midi(nmat, output_filename, midi_file=None,
                        ticks_per_beat=480, tempo=500000):
    """Wrapper for orchestrated_nmat_to_midi"""
    orchestrated_nmat_to_midi(nmat, output_filename,
                               midi_file=midi_file,
                               ticks_per_beat=ticks_per_beat,
                               tempo=tempo)
