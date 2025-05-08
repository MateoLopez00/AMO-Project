import mido
import numpy as np


def midi_to_nmat(filename):
    """
    Read a MIDI file and return a dictionary containing:
      - 'ticks_per_beat': int
      - 'type': int (MIDI file type)
      - 'tempo_events': list of (abs_tick, tempo)
      - 'notes': numpy array of shape (N, 5) with columns:
          [start_tick, duration_ticks, channel, pitch, velocity]
    """
    mid = mido.MidiFile(filename)
    ticks_per_beat = mid.ticks_per_beat
    type_ = mid.type

    # Extract tempo change events from first track
    tempo_events = []
    abs_tick = 0
    for msg in mid.tracks[0]:
        abs_tick += msg.time
        if msg.type == 'set_tempo':
            tempo_events.append((abs_tick, msg.tempo))

    # Extract note events from all tracks
    nmat_list = []
    for track in mid.tracks:
        abs_tick = 0
        ongoing = {}  # key=(channel,pitch) -> start_tick, velocity
        for msg in track:
            abs_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                ongoing[(msg.channel, msg.note)] = (abs_tick, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in ongoing:
                    start_tick, velocity = ongoing.pop(key)
                    duration = abs_tick - start_tick
                    nmat_list.append([start_tick, duration, msg.channel, msg.note, velocity])
    notes = np.array(nmat_list, dtype=int)

    return {
        'ticks_per_beat': ticks_per_beat,
        'type': type_,
        'tempo_events': tempo_events,
        'notes': notes
    }


def nmat_to_midi(nmat_data, output_filename):
    """
    Write a MIDI file from the dictionary produced by midi_to_nmat.
    - Preserves original file type, ticks_per_beat, and tempo events.
    - Writes only note-on/off events from nmat_data['notes'].
    """
    mid = mido.MidiFile(type=nmat_data['type'], ticks_per_beat=nmat_data['ticks_per_beat'])
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Write tempo meta-messages
    last_tick = 0
    for tick, tempo in sorted(nmat_data['tempo_events'], key=lambda x: x[0]):
        delta = tick - last_tick
        track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=delta))
        last_tick = tick

    # Build and sort note events
    events = []  # (abs_tick, kind, channel, pitch, velocity)
    for start, duration, ch, pitch, vel in nmat_data['notes']:
        events.append((start,  'note_on',  ch, pitch, vel))
        events.append((start + duration, 'note_off', ch, pitch, 0))
    events.sort(key=lambda e: (e[0], 0 if e[1]=='note_off' else 1))

    # Write note events with proper delta times
    prev_tick = last_tick  # continue after last tempo event
    for abs_tick, kind, ch, pitch, vel in events:
        delta = abs_tick - prev_tick
        if kind == 'note_on':
            msg = mido.Message('note_on', channel=ch, note=pitch, velocity=vel, time=delta)
        else:
            msg = mido.Message('note_off', channel=ch, note=pitch, velocity=0, time=delta)
        track.append(msg)
        prev_tick = abs_tick

    mid.save(output_filename)
