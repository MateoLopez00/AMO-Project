import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

def midi_to_nmat_with_channels(midi_file):
    """
    Read a MIDI file using mido and convert it to:
      1) a notematrix (nmat) with proper channel data, and
      2) dictionaries for channel->program and channel->track_name.
    
    nmat rows:
      [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec]
    """
    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat

    # Default tempo is 500000 microseconds/beat (120 BPM)
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break
    spb = tempo / 1e6  # seconds per beat

    # We store the last known program and track name for each channel
    channel_to_program = {}
    channel_to_track_name = {}

    # Merge all tracks so we can process them in time order
    merged = mido.merge_tracks(mid.tracks)
    current_ticks = 0

    nmat_list = []
    ongoing_notes = {}  # key=(channel, note) -> (start_sec, velocity)

    for msg in merged:
        current_ticks += msg.time
        current_sec = (current_ticks / ticks_per_beat) * spb
        
        # Update tempo if a tempo change occurs
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            spb = tempo / 1e6
        
        # If there's a program change, store it
        if msg.type == 'program_change':
            channel_to_program[msg.channel] = msg.program
        
        # If there's a track name meta, you can store it as well
        if msg.type == 'track_name':
            # The actual channel is ambiguous for track_name in raw MIDI,
            # but you can store it by your own track index if desired.
            # We'll just store a "global" track name or channel 0 here for demonstration.
            channel_to_track_name[0] = msg.name

        # Note on (velocity>0) = note start
        if msg.type == 'note_on' and msg.velocity > 0:
            key = (msg.channel, msg.note)
            ongoing_notes[key] = (current_sec, msg.velocity)

        # Note off or note_on with velocity=0 = note end
        elif msg.type in ('note_off', 'note_on') and msg.velocity == 0:
            key = (msg.channel, msg.note)
            if key in ongoing_notes:
                start_sec, velocity = ongoing_notes[key]
                duration_sec = current_sec - start_sec
                onset_beat = start_sec / spb
                duration_beat = duration_sec / spb
                nmat_list.append([
                    onset_beat, duration_beat, msg.channel, msg.note, 
                    velocity, start_sec, duration_sec
                ])
                del ongoing_notes[key]

    # Convert list to numpy array and sort
    nmat = np.array(nmat_list) if nmat_list else np.zeros((0,7))
    if nmat.size > 0:
        sort_idx = np.lexsort((nmat[:,3], nmat[:,0]))  # sort by pitch then onset
        nmat = nmat[sort_idx]

    return nmat, channel_to_program, channel_to_track_name

def nmat_to_midi(nmat, output_midi_file,
                 channel_to_program=None,
                 channel_to_track_name=None,
                 ticks_per_beat=480, tempo=500000):
    """
    Convert a notematrix (nmat) to a MIDI file using mido.
    Insert program changes for each channel at time=0 if available.
    Also insert track_name meta if you want staff labeling in certain DAWs/notation apps.
    """
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    
    if channel_to_program is None:
        channel_to_program = {}
    if channel_to_track_name is None:
        channel_to_track_name = {}

    spb = tempo / 1e6  # seconds per beat

    # Create a list of note events (time in seconds)
    events = []
    for row in nmat:
        onset_sec = row[5]
        duration_sec = row[6]
        off_sec = onset_sec + duration_sec
        channel = int(row[2])
        note = int(row[3])
        velocity = int(row[4])

        # Add note_on and note_off
        events.append((onset_sec, 'note_on', channel, note, velocity))
        events.append((off_sec, 'note_off', channel, note, 0))

    # Sort events by time; note_off before note_on if same time
    events.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))

    # Create the new MIDI file and track
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    # Insert tempo at time=0
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # Optional: Insert track name meta (if you want a single track name)
    if 0 in channel_to_track_name:
        track_name = channel_to_track_name[0]
        track.append(MetaMessage('track_name', name=track_name, time=0))

    # Insert program_change messages for each channel at time=0
    for ch, prog in channel_to_program.items():
        track.append(Message('program_change', channel=ch, program=prog, time=0))

    # Build the actual note messages with correct delta times
    prev_time_sec = 0.0
    for event in events:
        current_time_sec = event[0]
        delta_sec = current_time_sec - prev_time_sec
        delta_ticks = int(round(delta_sec / spb * ticks_per_beat))
        
        etype = event[1]
        ch = event[2]
        note = event[3]
        vel = event[4]
        
        if etype == 'note_on':
            msg = Message('note_on', channel=ch, note=note, velocity=vel, time=delta_ticks)
        else:  # 'note_off'
            msg = Message('note_off', channel=ch, note=note, velocity=0, time=delta_ticks)

        track.append(msg)
        prev_time_sec = current_time_sec

    mid.save(output_midi_file)

def extract_channels(midi_file):
    """
    Extract a mapping from track index to MIDI channel using mido.
    Returns a dictionary mapping track indices to a channel.
    For each track, we take the first note_on/note_off message's channel,
    defaulting to 0 if none is found.
    """
    midi_mido = mido.MidiFile(midi_file)
    channels_mapping = {}
    for i, track in enumerate(midi_mido.tracks):
        channel = None
        for msg in track:
            if msg.type in ['note_on', 'note_off'] and hasattr(msg, 'channel'):
                channel = msg.channel
                break
        channels_mapping[i] = channel if channel is not None else 0
    return channels_mapping

def extract_midi_features(midi_file):
    score = converter.parse(midi_file)
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    channels_mapping = extract_channels(midi_file)
    
    note_list = []
    
    # Loop through each part in the Music21 score using enumerate.
    for i, part in enumerate(score.parts):
        # Use the corresponding channel from mido's mapping; default to 0.
        channel = channels_mapping.get(i, 0)
        
        for element in part.flat.notes:
            if isinstance(element, note.Note):
                start = element.offset
                end = element.offset + element.quarterLength
                note_list.append((
                    element.pitch.midi,
                    start,
                    end,
                    element.volume.velocity if element.volume.velocity is not None else 100,
                    channel
                ))
            elif isinstance(element, chord.Chord):
                for n in element:
                    start = element.offset
                    end = element.offset + element.quarterLength
                    note_list.append((
                        n.pitch.midi,
                        start,
                        end,
                        n.volume.velocity if n.volume.velocity is not None else 100,
                        channel
                    ))
    
    # Define a structured dtype for note data (using raw quarter lengths).
    note_dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('channel', np.int32)
    ])
    
    note_array = np.array(note_list, dtype=note_dtype)
    note_array = np.sort(note_array, order=['start', 'pitch'])
    return note_array

def get_meter(midi_file):
    """
    Extracts meter (time signature) information from a MIDI file using Music21.
    Returns a list of dictionaries for each time signature event.
    """
    score = converter.parse(midi_file)
    ts_list = score.flat.getElementsByClass(meter.TimeSignature)
    meters = []
    
    for ts in ts_list:
        meters.append({
            "numerator": ts.numerator,
            "denominator": ts.denominator,
            "time_in_beats": ts.offset  # Using raw quarter lengths.
        })
    
    meters.sort(key=lambda x: x["time_in_beats"])
    return meters