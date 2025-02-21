import numpy as np
from music21 import converter, instrument, note, chord, meter

def extract_midi_features(midi_file):
    score = converter.parse(midi_file)
    note_list = []
    
    # Loop through each part in the score.
    for part in score.parts:
        instr_obj = part.getInstrument()
        instr_name = instr_obj.instrumentName if instr_obj.instrumentName is not None else "Unknown"
        
        # Iterate through all notes/chords in a flattened part.
        for element in part.flat.notes:
            if isinstance(element, note.Note):
                start = element.offset
                end = element.offset + element.quarterLength
                note_list.append((element.pitch.midi, start, end,
                                  element.volume.velocity if element.volume.velocity is not None else 100,
                                  instr_name))
            elif isinstance(element, chord.Chord):
                for n in element:
                    start = element.offset
                    end = element.offset + element.quarterLength
                    note_list.append((n.pitch.midi, start, end,
                                      n.volume.velocity if n.volume.velocity is not None else 100,
                                      instr_name))
    
    # Define a structured dtype for our note data.
    note_dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('instrument', 'U50')  # Up to 50-character Unicode string.
    ])
    
    # Convert list of tuples to a NumPy structured array.
    note_array = np.array(note_list, dtype=note_dtype)
    
    # Optionally sort the array by start time and pitch.
    note_array = np.sort(note_array, order=['start', 'pitch'])
    return note_array

def get_meter(midi_file):
    """
    Extracts meter (time signature) information from a MIDI file using music21.
    
    Returns:
        List[Dict]: A list of dictionaries with meter information.
                    Each dictionary contains:
                    - "numerator": beats per measure
                    - "denominator": beat unit (e.g., 4 for quarter note)
                    - "time_in_beats": the beat at which the time signature occurs (using raw quarter lengths)
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
    
    # Sort meters by their occurrence in the piece
    meters.sort(key=lambda x: x["time_in_beats"])
    return meters
