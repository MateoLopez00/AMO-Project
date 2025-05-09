import mido
import pandas as pd
import numpy as np

# Baseline layer-to-instrument mapping (no combos)
layer_mapping = {
    'melody':  {'channel': 1, 'program': 40, 'instrument': 'Violin'},
    'harmony': {'channel': 2, 'program': 42, 'instrument': 'Cello'},
    'rhythm':  {'channel': 3, 'program': 32, 'instrument': 'Acoustic Bass'}
}


def apply_orchestration(note_df):
    """
    Baseline orchestration: bucket notes by pitch into three layers:
      - melody  (>60)
      - harmony (50-60)
      - rhythm  (<50)
    Then assign each layer a fixed MIDI channel, GM program, and name.
    Adds new_channel, new_program, new_instrument columns.
    """
    new_channels = []
    new_programs = []
    new_instruments = []

    for _, row in note_df.iterrows():
        pitch = row['pitch']
        # Determine layer by pitch
        if pitch > 60:
            layer = 'melody'
        elif pitch >= 50:
            layer = 'harmony'
        else:
            layer = 'rhythm'
        info = layer_mapping[layer]
        new_channels.append(info['channel'])
        new_programs.append(info['program'])
        new_instruments.append(info['instrument'])

    note_df['new_channel'] = new_channels
    note_df['new_program'] = new_programs
    note_df['new_instrument'] = new_instruments
    return note_df


def orchestrated_nmat_to_midi(nmat, output_filename, midi_file=None,
                               ticks_per_beat=480, tempo=500000):
    """
    Converts an enriched note-matrix (>=12 cols) to MIDI,
    preserving metadata if midi_file is provided.
    """
    # Ensure enriched matrix (>=11 cols)
    if nmat.shape[1] == 9:
        raise ValueError("Note matrix must include new_channel and new_program columns.")

    # Prepare MidiFile
    if midi_file:
        orig = mido.MidiFile(midi_file)
        mid = mido.MidiFile(type=orig.type,
                            ticks_per_beat=orig.ticks_per_beat)
        track = mido.MidiTrack(); mid.tracks.append(track)
        # Copy meta-events
        for msg in orig.tracks[0]:
            if msg.is_meta and msg.type != 'end_of_track':
                track.append(msg.copy(time=msg.time))
    else:
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack(); mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    # Build note events in ticks
    events = []
    for row in nmat:
        start_q = row[7]  # onset_quarters
        dur_q   = row[8]  # duration_quarters
        start_tick = int(round(start_q * mid.ticks_per_beat))
        dur_ticks  = int(round(dur_q * mid.ticks_per_beat))
        off_tick   = start_tick + dur_ticks
        ch         = int(row[9]) - 1
        note       = int(row[3])
        vel        = int(row[4])
        events.append((start_tick, False, ch, note, vel))
        events.append((off_tick,   True,  ch, note, 0))
    events.sort(key=lambda e: (e[0], e[1]))

    # Program changes: one per channel
    used = {}
    for row in nmat:
        ch = int(row[9]) - 1; prog = int(row[10])
        if ch not in used:
            used[ch] = prog
    for ch, prog in used.items():
        track.append(mido.Message('program_change', channel=ch, program=prog, time=0))

    # Write notes
    last_tick = 0
    for abs_tick, is_off, ch, note, vel in events:
        delta = abs_tick - last_tick
        if not is_off:
            msg = mido.Message('note_on', channel=ch, note=note, velocity=vel, time=delta)
        else:
            msg = mido.Message('note_off', channel=ch, note=note, velocity=0, time=delta)
        track.append(msg)
        last_tick = abs_tick

    track.append(mido.MetaMessage('end_of_track', time=0))
    mid.save(output_filename)


def write_array_to_midi(nmat, output_filename, midi_file=None,
                        ticks_per_beat=480, tempo=500000):
    """Wrapper for orchestrated_nmat_to_midi"""
    orchestrated_nmat_to_midi(nmat, output_filename,
                               midi_file=midi_file,
                               ticks_per_beat=ticks_per_beat,
                               tempo=tempo)
