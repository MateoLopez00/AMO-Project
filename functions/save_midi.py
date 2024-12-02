import pretty_midi

def save_predictions_to_midi(predictions, input_features, output_file):
    """
    Saves the model's predictions as a MIDI file, with notes assigned to instruments
    based on their pitch range.

    Parameters:
        predictions (array): Predicted instrument labels for each note.
        input_features (array): Original piano note features (pitch, velocity, etc.).
        output_file (str): Path to save the output MIDI file.
    """
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()

    # Define pitch ranges for instruments
    instrument_ranges = {
        "violin": (55, 84),  # G3 to C7
        "cello": (36, 60),   # C2 to B3
        "flute": (60, 96),   # C4 to C7
        "clarinet": (50, 80) # D3 to G6
        # Add more instruments as needed
    }

    # Map instrument names to MIDI program numbers
    instrument_programs = {
        "violin": 40,
        "cello": 42,
        "flute": 73,
        "clarinet": 71
    }

    # Create instruments
    instruments = {name: pretty_midi.Instrument(program=program)
                   for name, program in instrument_programs.items()}

    # Iterate through predictions and features
    for i, (prediction, features) in enumerate(zip(predictions.flatten(), input_features)):
        pitch = int(features[3])  # Assume pitch is the 4th feature
        velocity = int(features[4])  # Assume velocity is the 5th feature
        start_time = features[0]  # Onset in seconds
        duration = features[1]  # Duration in seconds

        # Assign note to an instrument based on pitch range
        for instrument_name, (low, high) in instrument_ranges.items():
            if low <= pitch <= high:
                note = pretty_midi.Note(velocity=velocity, pitch=pitch,
                                         start=start_time, end=start_time + duration)
                instruments[instrument_name].notes.append(note)
                break  # Note is assigned to one instrument only

    # Add instruments to the MIDI file
    for instrument in instruments.values():
        if instrument.notes:  # Only add instruments with notes
            midi.instruments.append(instrument)

    # Save the MIDI file
    midi.write(output_file)
    print(f"Saved predicted orchestral MIDI file to: {output_file}")
