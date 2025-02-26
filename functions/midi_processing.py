import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi

def extract_midi_features(midi_file):
    score = converter.parse(midi_file)
    midi_data = pretty_midi.PrettyMIDI(midi_file)  # Use PrettyMIDI to extract channel info
    note_list = []
    
    # Loop through each part in the score, using enumerate to get the part index.
    for i, part in enumerate(score.parts):
        # Use the corresponding PrettyMIDI instrument, if available.
        if i < len(midi_data.instruments):
            channel = midi_data.instruments[i].channel
        else:
            channel = -1
        
        # Process all notes/chords in the part.
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
    
    # Define a structured dtype including the 'channel' field.
    note_dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('channel', np.int32)
    ])
    
    # Convert the list of tuples to a NumPy structured array.
    note_array = np.array(note_list, dtype=note_dtype)
    note_array = np.sort(note_array, order=['start', 'pitch'])
    return note_array

def get_meter(midi_file):
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
