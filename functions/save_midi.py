import pretty_midi

def save_predictions_to_midi(predictions, output_file, seq_len=50, feature_dim=6):
    """
    Saves the model's predictions as a MIDI file.

    Parameters:
        predictions (array): Predicted labels for orchestration (e.g., instrument program).
        output_file (str): Path to save the output MIDI file.
        seq_len (int): Length of each sequence.
        feature_dim (int): Number of features in the input.
    """
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()

    # Create instruments
    instrument_dict = {}
    for i in range(128):  # MIDI allows up to 128 instruments
        instrument_dict[i] = pretty_midi.Instrument(program=i)

    # Add notes to the corresponding instruments
    for time_idx, note_prediction in enumerate(predictions.flatten()):
        program = note_prediction
        pitch = 60  # Example: Middle C; you can make this dynamic based on your input
        velocity = 100
        start_time = time_idx / seq_len  # Example: distribute over sequence length
        duration = 0.5  # Example fixed duration

        # Create a PrettyMIDI note
        note = pretty_midi.Note(velocity=velocity, pitch=pitch,
                                 start=start_time, end=start_time + duration)

        # Add the note to the corresponding instrument
        instrument_dict[program].notes.append(note)

    # Add all instruments to the MIDI object
    for program, instrument in instrument_dict.items():
        if instrument.notes:  # Only add instruments with notes
            midi.instruments.append(instrument)

    # Write the MIDI file
    midi.write(output_file)
    print(f"Saved predicted orchestral MIDI file to: {output_file}")
