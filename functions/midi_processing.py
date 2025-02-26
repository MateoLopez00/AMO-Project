import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

def extract_channels(midi_file):
    """
    Extract a mapping from track index to MIDI channel using mido.
    Returns a dictionary where keys are track indices and values are channel numbers.
    If no channel is found, the value is -1.
    """
    midi_mido = mido.MidiFile(midi_file)
    channels_mapping = {}
    for i, track in enumerate(midi_mido.tracks):
        channels = set()
        for msg in track:
            if msg.type in ['note_on', 'note_off'] and hasattr(msg, 'channel'):
                channels.add(msg.channel)
        # If channels were found, take the first one; otherwise, default to -1.
        channels_mapping[i] = list(channels)[0] if channels else -1
    return channels_mapping

def extract_midi_features(midi_file):
    score = converter.parse(midi_file)
    # Also create a PrettyMIDI object (if needed for other info)
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    # Use mido to extract channel mapping.
    channels_mapping = extract_channels(midi_file)
    
    note_list = []
    
    # Loop through each part in the Music21 score using enumerate.
    for i, part in enumerate(score.parts):
        # Get the channel from the mido mapping; if not available, default to -1.
        channel = channels_mapping.get(i, -1)
        
        # Process all notes/chords in this part.
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
    
    # Define a structured dtype that includes the 'channel' field.
    note_dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('channel', np.int32)
    ])
    
    # Convert the list of tuples into a NumPy structured array.
    note_array = np.array(note_list, dtype=note_dtype)
    note_array = np.sort(note_array, order=['start', 'pitch'])
    return note_array

def get_meter(midi_file):
    """
    Extracts meter (time signature) information from a MIDI file using Music21.
    
    Returns a list of dictionaries, each containing:
      - "numerator": beats per measure
      - "denominator": beat unit (e.g., 4 for quarter note)
      - "time_in_beats": the offset (in raw quarter lengths) at which the time signature occurs
    """
    score = converter.parse(midi_file)
    ts_list = score.flat.getElementsByClass(meter.TimeSignature)
    meters = []
    
    for ts in ts_list:
        meters.append({
            "numerator": ts.numerator,
            "denominator": ts.denominator,
            "time_in_beats": ts.offset
        })
    
    meters.sort(key=lambda x: x["time_in_beats"])
    return meters
