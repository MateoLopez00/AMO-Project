import mido
import numpy as np


def midi_to_nmat(filename):
    """
    Read a MIDI file and return a dictionary containing:
      - 'ticks_per_beat': int
      - 'type': int (MIDI file type)
      - 'meta_events': list of (abs_tick, MetaMessage) for all meta events in any track
      - 'notes': numpy array of shape (N, 5) with columns:
          [start_tick, duration_ticks, channel, pitch, velocity]
    """
    mid = mido.MidiFile(filename)
    ticks_per_beat = mid.ticks_per_beat
    type_ = mid.type

    # Extract all meta messages from the first track only
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

    # Sort meta events by tick
    meta_events.sort(key=lambda x: x[0])

    return {
        'ticks_per_beat': ticks_per_beat,
        'type': type_,
        'meta_events': meta_events,
        'notes': notes
    }


def nmat_to_midi(nmat_data, output_filename):
    """
    Write a MIDI file from the dictionary produced by midi_to_nmat.
    - Preserves original file type, ticks_per_beat, and all meta events in a dedicated meta track.
    - Writes note-on/off events in a second track.
    """
    # Create new MidiFile with two tracks (meta + notes)
    mid = mido.MidiFile(type=nmat_data['type'],
                        ticks_per_beat=nmat_data['ticks_per_beat'])
    meta_track = mido.MidiTrack()
    note_track = mido.MidiTrack()
    mid.tracks.append(meta_track)
    mid.tracks.append(note_track)

    # 1) Write all meta events into meta_track
    prev_tick = 0
    for tick, msg in nmat_data['meta_events']:
        delta = tick - prev_tick
        meta_track.append(msg.copy(time=delta))
        prev_tick = tick
    meta_track.append(mido.MetaMessage('end_of_track', time=0))

    # 2) Collect note-on/off events
    events = []  # (abs_tick, kind, channel, pitch, velocity)
    for start, duration, ch, pitch, vel in nmat_data['notes']:
        events.append((start,        'note_on',  ch, pitch, vel))
        events.append((start+duration,'note_off', ch, pitch, 0))
    # Sort by time, note_off before note_on at same tick
    events.sort(key=lambda e: (e[0], 0 if e[1]=='note_off' else 1))

    # 3) Write note events into note_track
    prev_tick = 0
    for abs_tick, kind, ch, pitch, vel in events:
        delta = abs_tick - prev_tick
        if kind == 'note_on':
            msg = mido.Message('note_on', channel=ch, note=pitch, velocity=vel, time=delta)
        else:
            msg = mido.Message('note_off', channel=ch, note=pitch, velocity=0, time=delta)
        note_track.append(msg)
        prev_tick = abs_tick
    note_track.append(mido.MetaMessage('end_of_track', time=0))

    # Save file
    mid.save(output_filename)
