# midi_processing.py
import mido
import numpy as np
import pandas as pd

def read_midi_full(filename):
    """
    Reads a MIDI file track by track, preserving:
      - All MIDI messages (with absolute tick times)
      - Ticks per beat
      - Each track's events in their original order
      - Builds a 'notematrix' from the note_on/off messages for analysis.
      
    Returns:
      - midi_data: A dict with keys 'ticks_per_beat', 'tracks' (each a dict with an 'events' list),
                   and 'type' (MIDI file type).
      - nmat: An (N x 7) NumPy array of note data 
              [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec]
    """
    mid = mido.MidiFile(filename)
    ticks_per_beat = mid.ticks_per_beat

    tracks_data = []
    nmat_list = []

    default_tempo = 500000  # 120 BPM in microseconds per beat

    for i, track in enumerate(mid.tracks):
        abs_ticks = 0
        current_tempo = default_tempo
        events = []
        ongoing_notes = {}  # key=(channel, note) -> (start_tick, start_sec, velocity, tempo_when_started)

        for msg in track:
            abs_ticks += msg.time
            events.append((abs_ticks, msg))

        events.sort(key=lambda x: x[0])
        events_with_sec = []
        last_ticks = 0
        last_sec = 0.0
        current_tempo = default_tempo

        for (tick_val, msg) in events:
            delta_ticks = tick_val - last_ticks
            delta_sec = delta_ticks * (current_tempo / 1e6) / ticks_per_beat
            current_sec = last_sec + delta_sec

            if msg.type == 'set_tempo':
                current_tempo = msg.tempo

            if msg.type in ('note_on', 'note_off'):
                channel = getattr(msg, 'channel', 0)
                note = getattr(msg, 'note', 0)
                velocity = getattr(msg, 'velocity', 0)
                if msg.type == 'note_on' and velocity > 0:
                    ongoing_notes[(channel, note)] = (tick_val, current_sec, velocity, current_tempo)
                else:
                    key = (channel, note)
                    if key in ongoing_notes:
                        start_tick, start_sec, start_vel, start_tempo = ongoing_notes[key]
                        dur_ticks = tick_val - start_tick
                        dur_sec = current_sec - start_sec
                        onset_beats = start_tick / ticks_per_beat
                        duration_beats = dur_ticks / ticks_per_beat
                        nmat_list.append([
                            onset_beats, duration_beats, channel, note, start_vel, start_sec, dur_sec
                        ])
                        del ongoing_notes[key]

            events_with_sec.append((tick_val, current_sec, msg))
            last_ticks = tick_val
            last_sec = current_sec

        tracks_data.append({
            'track_index': i,
            'events': events_with_sec
        })

    if nmat_list:
        nmat = np.array(nmat_list)
        sort_idx = np.lexsort((nmat[:, 3], nmat[:, 0]))
        nmat = nmat[sort_idx]
    else:
        nmat = np.zeros((0, 7))

    midi_data = {
        'ticks_per_beat': ticks_per_beat,
        'tracks': tracks_data,
        'type': mid.type
    }
    return midi_data, nmat

def write_midi_full(midi_data, output_filename):
    """
    Reconstructs a MIDI file from the full track data (midi_data) as captured by read_midi_full.
    All messages and track ordering are preserved.
    """
    from mido import MidiFile, MidiTrack
    mid = MidiFile(ticks_per_beat=midi_data['ticks_per_beat'], type=midi_data['type'])

    for track_dict in midi_data['tracks']:
        track = MidiTrack()
        mid.tracks.append(track)
        events = track_dict['events']
        events = sorted(events, key=lambda e: e[0])
        last_tick = 0
        for (abs_tick, abs_sec, msg) in events:
            delta = abs_tick - last_tick
            last_tick = abs_tick
            new_msg = msg.copy(time=delta)
            track.append(new_msg)
    mid.save(output_filename)

def roundtrip_example(input_midi, output_midi, comparison_xlsx="comparison.xlsx"):
    """
    Performs a roundtrip:
      1. Reads the input MIDI file (capturing full track data and building a notematrix)
      2. Writes a new MIDI file from that data.
      3. Reads back the new MIDI to build a new notematrix.
      4. Writes an Excel file comparing the original and new notematrices.
    """
    midi_data, nmat_in = read_midi_full(input_midi)
    write_midi_full(midi_data, output_midi)
    midi_data_out, nmat_out = read_midi_full(output_midi)

    columns_in = ["in_onset_beats", "in_duration_beats", "in_channel", "in_pitch", "in_velocity", "in_onset_sec", "in_duration_sec"]
    columns_out = ["out_onset_beats", "out_duration_beats", "out_channel", "out_pitch", "out_velocity", "out_onset_sec", "out_duration_sec"]

    import_df = pd.DataFrame(nmat_in, columns=columns_in)
    export_df = pd.DataFrame(nmat_out, columns=columns_out)

    import_df = import_df.sort_values(by=["in_onset_beats", "in_pitch"]).reset_index(drop=True)
    export_df = export_df.sort_values(by=["out_onset_beats", "out_pitch"]).reset_index(drop=True)

    max_len = max(len(import_df), len(export_df))
    import_df = import_df.reindex(range(max_len))
    export_df = export_df.reindex(range(max_len))
    blank_col = pd.DataFrame({"": [""] * max_len})
    comparison_df = pd.concat([import_df, blank_col, export_df], axis=1)
    comparison_df.to_excel(comparison_xlsx, index=False)

    print(f"Done. Wrote new MIDI to {output_midi}, comparison to {comparison_xlsx}.")
