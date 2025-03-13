import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

def midi_to_array(midi_file):
    """
    Reads a MIDI file using mido and extracts note features into a NumPy structured array.
    The array will contain the columns: pitch, start, end, velocity, channel, track.
    Start and end are computed in beats (quarter lengths), using the file's ticks_per_beat.
    """
    from mido import MidiFile
    mid = MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat
    note_events = []
    
    # Process each track separately to preserve track info.
    for track_index, track in enumerate(mid.tracks):
        current_tick = 0
        active_notes = {}  # key: (pitch, channel) -> list of start ticks
        for msg in track:
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.note, msg.channel)
                active_notes.setdefault(key, []).append(current_tick)
            elif msg.type in ['note_off'] or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.note, msg.channel)
                if key in active_notes and active_notes[key]:
                    start_tick = active_notes[key].pop(0)
                    start_beat = start_tick / ticks_per_beat
                    end_beat = current_tick / ticks_per_beat
                    note_events.append((msg.note, start_beat, end_beat, msg.velocity, msg.channel, track_index))
        # If some active notes remain, we ignore them.
    # Sort events by start then by pitch.
    note_events.sort(key=lambda x: (x[1], x[0]))
    dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('channel', np.int32),
        ('track', np.int32)
    ])
    return np.array(note_events, dtype=dtype)

def array_to_midi(note_array, output_file, ticks_per_beat=480, tempo=500000):
    """
    Converts a note array (with fields: pitch, start, end, velocity, channel, track)
    back into a MIDI file and writes it to output_file.
    Beats (quarter lengths) are converted back to ticks using ticks_per_beat.
    A default tempo meta message is added to track 0.
    """
    from mido import Message, MidiFile, MidiTrack, MetaMessage
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    # Group note events by track.
    tracks_dict = {}
    for note in note_array:
        track_idx = int(note['track'])
        tracks_dict.setdefault(track_idx, []).append(note)
    
    # For each original track, create a MidiTrack and add events.
    for track_idx, notes in tracks_dict.items():
        track = MidiTrack()
        mid.tracks.append(track)
        # Convert beat times to ticks.
        events = []
        for note in notes:
            start_tick = int(round(note['start'] * ticks_per_beat))
            end_tick = int(round(note['end'] * ticks_per_beat))
            events.append((start_tick, 'note_on', int(note['pitch']), int(note['velocity']), int(note['channel'])))
            events.append((end_tick, 'note_off', int(note['pitch']), int(note['velocity']), int(note['channel'])))
        # Sort events by absolute tick time.
        events.sort(key=lambda x: x[0])
        prev_tick = 0
        for evt in events:
            tick, etype, pitch, velocity, channel = evt
            delta = tick - prev_tick
            prev_tick = tick
            msg = Message(etype, note=pitch, velocity=velocity, channel=channel, time=delta)
            track.append(msg)
    # Insert a tempo meta message at the beginning of track 0.
    if mid.tracks:
        mid.tracks[0].insert(0, MetaMessage('set_tempo', tempo=tempo, time=0))
    mid.save(output_file)

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
