import mido
import numpy as np


def midi_to_nmat(filename):
    """
    Read a MIDI file and return a dictionary containing:
      - 'ticks_per_beat': int
      - 'type': int (MIDI file type)
      - 'meta_events': list of (abs_tick, MetaMessage) for all meta events in track 0
      - 'notes': numpy array of shape (N, 5) with columns:
          [start_tick, duration_ticks, channel, pitch, velocity]
    """
    mid = mido.MidiFile(filename)
    ticks_per_beat = mid.ticks_per_beat
    type_ = mid.type

    # Extract all meta messages from the first track
    meta_events = []
    abs_tick = 0
    for msg in mid.tracks[0]:
        abs_tick += msg.time
        if msg.is_meta:
            meta_events.append((abs_tick, msg.copy()))

    # Extract note events from all tracks
    nmat_list = []
    for track in mid.tracks:
        abs_tick = 0
        ongoing = {}  # key=(channel,pitch) -> (start_tick, velocity)
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
        'meta_events': meta_events,
        'notes': notes
    }


def nmat_to_midi(nmat_data, output_filename):
    """
    Write a MIDI file from the dictionary produced by midi_to_nmat.
    - Preserves original file type, ticks_per_beat, and all meta events from track 0.
    - Writes only note-on/off events from nmat_data['notes'], merging them with meta events in one track.
    """
    mid = mido.MidiFile(type=nmat_data['type'], ticks_per_beat=nmat_data['ticks_per_beat'])
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Build combined event list: (abs_tick, priority, data)
    events = []
    # Meta events: priority 0
    for tick, msg in nmat_data['meta_events']:
        events.append((tick, 0, msg))
    # Note events: priority 1
    for start, duration, ch, pitch, vel in nmat_data['notes']:
        events.append((start,        1, ('on',  ch, pitch, vel)))
        events.append((start+duration,1, ('off', ch, pitch, 0)))
    # Sort by absolute tick, then meta before notes
    events.sort(key=lambda e: (e[0], e[1]))

    # Write events with proper delta times
    prev_tick = 0
    for abs_tick, prio, data in events:
        delta = abs_tick - prev_tick
        if prio == 0:
            # meta message
            meta = data.copy(time=delta)
            track.append(meta)
        else:
            kind, ch, pitch, vel = data
            if kind == 'on':
                msg = mido.Message('note_on', channel=ch, note=pitch, velocity=vel, time=delta)
            else:
                msg = mido.Message('note_off', channel=ch, note=pitch, velocity=vel, time=delta)
            track.append(msg)
        prev_tick = abs_tick

    mid.save(output_filename)
