# midi_utils.py
import mido
import numpy as np

def midi_to_nmat_with_channels(midi_file):
    """
    Reads a MIDI file using mido and returns a notematrix (nmat) where each row is:
      [onset_beats, duration_beats, original_channel, pitch, velocity, onset_sec, duration_sec]
    This simplified version assumes a single constant tempo.
    """
    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000  
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break
    spb = tempo / 1e6  # seconds per beat

    current_ticks = 0
    nmat_list = []
    ongoing_notes = {}
    
    # Merge all tracks for note extraction
    merged = mido.merge_tracks(mid.tracks)
    for msg in merged:
        current_ticks += msg.time
        current_sec = (current_ticks / ticks_per_beat) * spb
        
        if msg.type == 'note_on' and msg.velocity > 0:
            key = (msg.channel, msg.note)
            ongoing_notes[key] = (current_sec, msg.velocity)
        elif msg.type in ('note_off', 'note_on') and msg.velocity == 0:
            key = (msg.channel, msg.note)
            if key in ongoing_notes:
                start_sec, velocity = ongoing_notes[key]
                duration_sec = current_sec - start_sec
                onset_beats = start_sec / spb
                duration_beats = duration_sec / spb
                nmat_list.append([onset_beats, duration_beats, msg.channel, msg.note, velocity, start_sec, duration_sec])
                del ongoing_notes[key]
    
    if nmat_list:
        nmat = np.array(nmat_list)
        sort_idx = np.lexsort((nmat[:, 3], nmat[:, 0]))
        nmat = nmat[sort_idx]
    else:
        nmat = np.zeros((0,7))
    return nmat

def orchestrated_nmat_to_midi(nmat, output_midi_file, ticks_per_beat=480, tempo=500000):
    """
    Converts an orchestrated notematrix (which must now have 9 columns, where columns 7 and 8
    are 'new_channel' and 'new_program') back to a MIDI file.
    Inserts program_change messages at time=0 for each new channel.
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
    
    # Insert tempo meta message
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Insert program_change messages for each unique new channel
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
        if event[1]=='note_on':
            msg = mido.Message('note_on', channel=event[2], note=event[3], velocity=event[4], time=delta_ticks)
        else:
            msg = mido.Message('note_off', channel=event[2], note=event[3], velocity=0, time=delta_ticks)
        track.append(msg)
        prev_time_sec = current_time_sec
    mid.save(output_midi_file)
