# midi_processing.py using music21
from music21 import converter, instrument, note, chord, meter

def extract_midi_features(midi_file):
    """
    Extract note features from a MIDI file using music21.
    
    Returns:
        List[Dict]: A list of dictionaries with note features.
                    Each dictionary contains:
                    - "pitch": MIDI pitch number
                    - "start": onset time in beats (quarter lengths)
                    - "end": offset time in beats (quarter lengths)
                    - "velocity": note velocity (defaulted to 100 if unavailable)
                    - "instrument": instrument name (extracted from the part)
    """
    score = converter.parse(midi_file)
    note_features = []
    
    # Loop through each part in the score
    for part in score.parts:
        # Try to get an instrument from the part; default to "Unknown" if not available
        instr_obj = part.getInstrument()
        instr_name = instr_obj.instrumentName if instr_obj.instrumentName is not None else "Unknown"
        
        # Iterate through all notes/chords in a flattened part
        for element in part.flat.notes:
            # For single notes
            if isinstance(element, note.Note):
                note_features.append({
                    "pitch": element.pitch.midi,
                    "start": element.offset,  # music21 offset is in quarter lengths (beats)
                    "end": element.offset + element.quarterLength,
                    "velocity": element.volume.velocity if element.volume.velocity is not None else 100,
                    "instrument": instr_name
                })
            # For chords, add each note individually
            elif isinstance(element, chord.Chord):
                for n in element:
                    note_features.append({
                        "pitch": n.pitch.midi,
                        "start": element.offset,
                        "end": element.offset + element.quarterLength,
                        "velocity": n.volume.velocity if n.volume.velocity is not None else 100,
                        "instrument": instr_name
                    })
                    
    # Sort the list by start time then pitch for consistency with your current logic
    note_features.sort(key=lambda x: (x["start"], x["pitch"]))
    return note_features

def get_meter(midi_file):
    """
    Extracts meter (time signature) information from a MIDI file using music21.
    
    Returns:
        List[Dict]: A list of dictionaries with meter information.
                    Each dictionary contains:
                    - "numerator": beats per measure
                    - "denominator": beat unit (e.g., 4 for quarter note)
                    - "time_in_beats": the beat at which the time signature occurs
    """
    score = converter.parse(midi_file)
    ts_list = score.flat.getElementsByClass(meter.TimeSignature)
    meters = []
    
    for ts in ts_list:
        meters.append({
            "numerator": ts.numerator,
            "denominator": ts.denominator,
            "time_in_beats": ts.offset  # offset in quarter lengths (beats)
        })
    
    # Sort meters by their occurrence in the piece
    meters.sort(key=lambda x: x["time_in_beats"])
    return meters
