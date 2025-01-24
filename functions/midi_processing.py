import partitura
import pretty_midi

def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file using Partitura (symbolic data) 
    and Pretty MIDI (velocity).
    
    Args:
        midi_file (str): Path to the MIDI file.
    Returns:
        List[Dict]: A list of dictionaries with note features.
    """
    # Load symbolic data using Partitura
    score = partitura.load_score_midi(midi_file)
    note_array = partitura.utils.ensure_notearray(score)

    # Load performance data using Pretty MIDI
    midi_data = pretty_midi.PrettyMIDI(midi_file)

    # Create a list of dictionaries for note features
    note_features = []

    # Map Pretty MIDI notes by time and pitch
    pretty_notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            pretty_notes.append({
                "pitch": note.pitch,
                "start": note.start,
                "end": note.end,
                "velocity": note.velocity
            })

    # Sort Pretty MIDI notes by start time
    pretty_notes.sort(key=lambda x: (x["start"], x["pitch"]))

    # Combine Partitura's note_array with Pretty MIDI velocities
    for note in note_array:
        # Find the matching Pretty MIDI note (same pitch and time)
        matching_notes = [
            pn for pn in pretty_notes
            if abs(pn["start"] - note["onset_sec"]) < 0.01 and pn["pitch"] == note["pitch"]
        ]

        velocity = matching_notes[0]["velocity"] if matching_notes else 100  # Default to 100

        # Append the combined note attributes
        note_features.append({
            "pitch": note["pitch"],
            "start": note["onset_beat"],  # Timing in beats
            "end": note["onset_beat"] + note["duration_beat"],
            "velocity": velocity,
            "instrument": note["id_in_part"]
        })

    return note_features
