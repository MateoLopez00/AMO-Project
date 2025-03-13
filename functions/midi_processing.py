import numpy as np
from music21 import converter, note, chord, meter
import pretty_midi
import mido

def midi_to_nmat(midi_file):
    # Load the MIDI file using pretty_midi
    pm = pretty_midi.PrettyMIDI(midi_file)
    
    # Estimate tempo (in BPM) and compute seconds per beat
    tempo = pm.estimate_tempo()
    spb = 60.0 / tempo  # seconds per beat

    nmat_list = []
    for instrument in pm.instruments:
        # pretty_midi does not expose the MIDI channel directly.
        # We use a simple placeholder: if the instrument is a drum, assign channel 10 (MIDI channel 10 is 9 in 0-indexing);
        # otherwise, we use 1.
        channel = 10 if instrument.is_drum else 1
        for note in instrument.notes:
            onset_sec = note.start
            duration_sec = note.end - note.start
            onset_beat = onset_sec / spb
            duration_beat = duration_sec / spb

            # Append a row: [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec]
            nmat_list.append([onset_beat, duration_beat, channel, note.pitch, note.velocity, onset_sec, duration_sec])
    
    # Convert list to numpy array and sort by onset (if needed)
    nmat = np.array(nmat_list)
    nmat = nmat[np.argsort(nmat[:, 0])]
    return nmat

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