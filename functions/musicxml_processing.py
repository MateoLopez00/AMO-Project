from music21 import converter, note, chord, stream, tempo
import numpy as np

def read_mxl_full(filename):
    """
    Reads an MXL (MusicXML) file and builds a note matrix with columns:
      [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec]
    Note: MusicXML does not usually include explicit channel or velocity info, so default
    values are used (channel=0, velocity=64). Tempo is read from the score if available;
    otherwise, 120 BPM is assumed.
    """
    score = converter.parse(filename)
    # Attempt to get a tempo mark from the score; default to 120 BPM (500000 μs/beat)
    bpm = 120
    if score.metronomeMarkBoundaries():
        bpm = score.metronomeMarkBoundaries()[0][2].number
    sec_per_beat = 60.0 / bpm

    nmat_list = []
    # Iterate over parts
    for part in score.parts:
        # Flatten the part to get all note and chord objects
        for n in part.flat.notes:
            # Handle individual Note objects
            if isinstance(n, note.Note):
                onset_beats = n.offset
                duration_beats = n.quarterLength
                pitch_val = n.pitch.midi
                velocity = 64  # default velocity
                onset_sec = onset_beats * sec_per_beat
                duration_sec = duration_beats * sec_per_beat
                # MusicXML does not store MIDI channel information; default to 0.
                nmat_list.append([onset_beats, duration_beats, 0, pitch_val, velocity, onset_sec, duration_sec])
            # Expand Chord objects into separate notes
            elif isinstance(n, chord.Chord):
                for p in n.pitches:
                    onset_beats = n.offset
                    duration_beats = n.quarterLength
                    pitch_val = p.midi
                    velocity = 64
                    onset_sec = onset_beats * sec_per_beat
                    duration_sec = duration_beats * sec_per_beat
                    nmat_list.append([onset_beats, duration_beats, 0, pitch_val, velocity, onset_sec, duration_sec])
                    
    if nmat_list:
        nmat = np.array(nmat_list)
        sort_idx = np.lexsort((nmat[:, 3], nmat[:, 0]))
        nmat = nmat[sort_idx]
    else:
        nmat = np.zeros((0, 7))
        
    musicxml_data = {
        'score': score,
        'bpm': bpm
    }
    return musicxml_data, nmat

def orchestrated_nmat_to_mxl(nmat, output_filename, default_tempo=500000):
    """
    Converts an orchestrated note matrix (with 9 columns: the original 7 plus new_channel and new_program)
    into a MusicXML file (MXL). For each note, we create a music21 Note; we set its offset and quarterLength
    according to the note matrix. (We do not attempt to map GM patch numbers to specific instrument classes
    in MusicXML—this could be added if desired.)
    """
    from music21 import stream, note, instrument

    # Create a new score and part.
    score = stream.Score()
    part = stream.Part()
    score.insert(0, part)
    
    # Set tempo: convert microseconds per beat (default_tempo) to BPM.
    bpm = 60000000 / default_tempo
    mm = tempo.MetronomeMark(number=bpm)
    part.insert(0, mm)
    
    # For each row in the note matrix, create a music21 note.
    # nmat columns: [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec, new_channel, new_program]
    for row in nmat:
        onset_beats = row[0]
        duration_beats = row[1]
        pitch_val = int(row[3])
        # For MusicXML we ignore the new_channel/new_program since notation does not assign these the same way.
        n = note.Note()
        n.pitch.midi = pitch_val
        n.quarterLength = duration_beats
        n.offset = onset_beats
        part.append(n)
        
    # Write out the score as MusicXML.
    score.write('musicxml', fp=output_filename)
    print(f"Saved orchestrated MusicXML (MXL) to {output_filename}")
