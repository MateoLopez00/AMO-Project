import partitura
import pretty_midi

def extract_midi_features(midi_file):
    """
    Extracts note features from a MIDI file using Partitura for symbolic attributes
    and Pretty MIDI for velocity.
    
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

    # Calculate tempo to convert seconds to beats
    tempo = midi_data.get_tempo_changes()[1][0]  # Get the first tempo value
    seconds_to_beats = lambda seconds: seconds * tempo / 60.0

    # Map Partitura's note array to their parts
    part_map = {part.id: part for part in score.parts}

    # Create a list of dictionaries for note features
    note_features = []

    # Map Pretty MIDI notes by time and pitch
    pretty_notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            pretty_notes.append({
                "pitch": note.pitch,
                "start": seconds_to_beats(note.start),  # Convert seconds to beats
                "end": seconds_to_beats(note.end),      # Convert seconds to beats
                "velocity": note.velocity
            })

    # Sort Pretty MIDI notes by start time
    pretty_notes.sort(key=lambda x: (x["start"], x["pitch"]))

    # Combine Partitura's note_array with Pretty MIDI velocities
    for note in note_array:
        # Find the matching Pretty MIDI note (same pitch and time in beats)
        matching_notes = [
            pn for pn in pretty_notes
            if abs(pn["start"] - note["onset_beat"]) < 0.01 and pn["pitch"] == note["pitch"]
        ]

        velocity = matching_notes[0]["velocity"] if matching_notes else 100  # Default to 100

        # Get part (instrument) information
        part_id = note["id"]  # ID of the part in Partitura
        instrument = part_map[part_id].name if part_id in part_map else "Unknown"

        # Append the combined note attributes
        note_features.append({
            "pitch": note["pitch"],
            "start": note["onset_beat"],  # Timing in beats
            "end": note["onset_beat"] + note["duration_beat"],
            "velocity": velocity,
            "instrument": instrument  # Use Partitura's part name
        })

    return note_features

def get_meter_partitura(midi_file):
    """
    Extracts the meter (time signature) from a MIDI file using Partitura.
    
    Args:
        midi_file (str): Path to the MIDI file.

    Returns:
        List[Dict]: A list of dictionaries with meter information.
    """
    # Load the MIDI file as a performance to access the note array
    performance = partitura.load_performance_midi(midi_file)
    note_array = performance.note_array()

    # Use the PPQ (ticks per quarter note) to convert ticks to beats
    ppq = performance.ppq if hasattr(performance, "ppq") else 480  # Default to 480 if ppq is unavailable

    # Load the MIDI file as a score to extract time signatures
    score = partitura.load_score_midi(midi_file)

    # Collect time signatures
    meters = []
    for part in score.parts:
        for ts in part.iter_all(partitura.score.TimeSignature):
            # Convert the start time from ticks to beats
            start_time_in_beats = ts.start.t / ppq if ts.start else 0
            meters.append({
                "numerator": ts.beats,           # Beats per measure
                "denominator": ts.beat_type,    # Beat type (e.g., quarter note)
                "time_in_beats": start_time_in_beats  # Start time in beats
            })

    return meters

