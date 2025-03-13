import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

def extract_channels(midi_file):
    """
    Extract a mapping from track index to a list of MIDI channels using mido.
    For each track, we examine all note_on/note_off messages and store all unique channels.
    If no channel is found, we default to [0].
    """
    midi_mido = mido.MidiFile(midi_file)
    channels_mapping = {}
    for i, track in enumerate(midi_mido.tracks):
        channels = set()
        for msg in track:
            if msg.type in ['note_on', 'note_off'] and hasattr(msg, 'channel'):
                channels.add(msg.channel)
        # If no channels were found for this track, default to [0]
        channels_mapping[i] = list(channels) if channels else [0]
    return channels_mapping

def midi_to_array(midi_file):
    """
    Reads a MIDI file and extracts note features into a NumPy structured array.
    The array will contain the columns: pitch, start, end, velocity, channel.
    Note times are kept as raw quarter-length values (beats).
    The channel field is stored as an object (list of channels) to preserve all channel info.
    """
    midi_obj = pretty_midi.PrettyMIDI(midi_file)
    # Extract channels using mido.
    channels_mapping = extract_channels(midi_file)
    # Build a list of channels sorted by track index.
    sorted_indices = sorted(channels_mapping.keys())
    channels_list = [channels_mapping[i] for i in sorted_indices]
    
    note_list = []
    # Loop through each instrument in the PrettyMIDI object.
    # Note: The ordering of instruments may not perfectly match the mido track order.
    for i, instrument in enumerate(midi_obj.instruments):
        # Attempt to assign channel info:
        # First, try using channels_list[i+1] if available and non-empty, else channels_list[i], else default to [0].
        if (i+1) < len(channels_list) and len(channels_list[i+1]) > 0:
            channel = channels_list[i+1]
        elif i < len(channels_list) and len(channels_list[i]) > 0:
            channel = channels_list[i]
        else:
            channel = [0]
        for n in instrument.notes:
            note_list.append((n.pitch, n.start, n.end, n.velocity, channel))
    
    note_dtype = np.dtype([
        ('pitch', np.int32),
        ('start', np.float64),
        ('end', np.float64),
        ('velocity', np.int32),
        ('channel', object)  # store channel as object to allow a list
    ])
    note_array = np.array(note_list, dtype=note_dtype)
    note_array = np.sort(note_array, order=['start', 'pitch'])
    return note_array

def array_to_midi(note_array, output_file, tempo_times=None, tempos=None):
    """
    Converts a NumPy structured array (with fields: pitch, start, end, velocity, channel)
    back into a MIDI file and writes it to output_file.
    
    Optionally, if tempo_times and tempos are provided, they are added to the MIDI.
    
    Note: Since a MIDI note can only belong to one channel, if the channel field is a list,
    the function uses the first channel from the list.
    """
    midi_obj = pretty_midi.PrettyMIDI()
    instruments_dict = {}
    for note in note_array:
        # If the channel field is a list, take the first element.
        ch = note['channel'][0] if isinstance(note['channel'], list) and len(note['channel']) > 0 else 0
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
