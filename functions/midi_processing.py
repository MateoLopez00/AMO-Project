import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

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

def midi_to_array(midi_file):
    """
    Reads a MIDI file and extracts note features into a NumPy structured array.
    The array will contain the columns: pitch, start, end, velocity, channel.
    Note times are kept as raw quarter-length values (beats).
    """
    midi_obj = pretty_midi.PrettyMIDI(midi_file)
    # Extract channels using mido.
    channels_mapping = extract_channels(midi_file)
    # Build a list of channels sorted by track index.
    sorted_indices = sorted(channels_mapping.keys())
    channels_list = [channels_mapping[i] for i in sorted_indices]
    
    note_list = []
    # Loop through each instrument in the PrettyMIDI object.
    # We assume Music21 parts correspond to mido tracks starting at index 1.
    for i, instrument in enumerate(midi_obj.instruments):
        # Use channel from channels_list[i+1] if available, else default to 0.
        channel = channels_list[i+1] if (i+1) < len(channels_list) else 0
        for note in instrument.notes:
            note_list.append((note.pitch, note.start, note.end, note.velocity, channel))
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

def array_to_midi(note_array, output_file, tempo_times=None, tempos=None):
    """
    Converts a NumPy structured array (with fields: pitch, start, end, velocity, channel)
    back into a MIDI file and writes it to output_file.
    Optionally, if tempo_times and tempos are provided, they are added to the MIDI.
    """
    midi_obj = pretty_midi.PrettyMIDI()
    instruments_dict = {}
    for note in note_array:
        ch = int(note['channel'])
        if ch not in instruments_dict:
            instr = pretty_midi.Instrument(program=0, is_drum=False)
            instr.channel = ch
            instruments_dict[ch] = instr
        new_note = pretty_midi.Note(
            pitch=int(note['pitch']),
            start=float(note['start']),
            end=float(note['end']),
            velocity=int(note['velocity'])
        )
        instruments_dict[ch].notes.append(new_note)
    for instr in instruments_dict.values():
        instr.notes.sort(key=lambda n: n.start)
        midi_obj.instruments.append(instr)
    if tempo_times is not None and tempos is not None:
        midi_obj._PrettyMIDI__tempo_changes = (np.array(tempo_times), np.array(tempos))
    midi_obj.write(output_file)

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
