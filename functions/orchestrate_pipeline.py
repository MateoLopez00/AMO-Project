from midi_processing import read_midi_full, write_midi_full
from orchestration import apply_orchestration, orchestrated_nmat_to_midi
from evaluation import evaluate_orchestration, pitch_class_entropy, scale_consistency, average_polyphony
import pandas as pd
import matplotlib.pyplot as plt
from visualization import nmat_to_note_list_vis, plot_piano_roll, plot_polyphony

def orchestrate_pipeline(input_midi, output_midi, comparison_xlsx="comparison.xlsx"):
    # 1. Read the full MIDI and build its note matrix (nmat_in)
    midi_data, nmat_in = read_midi_full(input_midi)
    
    # 2. Convert the note matrix into a DataFrame (original has 7 columns)
    df = pd.DataFrame(nmat_in, columns=[
        "onset_beats", "duration_beats", "channel", "pitch", "velocity", "onset_sec", "duration_sec"
    ])
    
    # 3. Apply orchestration logic to assign new channels, GM patch numbers, and instrument names.
    #    This returns a DataFrame with 10 columns.
    df_orch = apply_orchestration(df)
    
    # 4. Convert the orchestrated DataFrame back to a notematrix (nmat_orch will be shape (N,10))
    nmat_orch = df_orch.to_numpy()
    
    # 5. Write out a new MIDI file using the orchestrated note matrix.
    #    (The MIDI file itself does not store our extra columns.)
    orchestrated_nmat_to_midi(nmat_orch, output_midi)
    
    # 6. For comparison, read back the newly created MIDI file.
    #    Note: read_midi_full() returns a 7-column note matrix (nmat_out) from the MIDI file.
    midi_data_out, nmat_out = read_midi_full(output_midi)
    
    # 7. Build DataFrames for side-by-side comparison.
    #    We want to show the original note matrix (7 columns) alongside our orchestrated DataFrame (10 columns).
    columns_in = ["in_onset_beats", "in_duration_beats", "in_channel", "in_pitch", "in_velocity", "in_onset_sec", "in_duration_sec"]
    # For the orchestrated output, we include our extra fields.
    columns_orch = [
        "out_onset_beats", "out_duration_beats", "out_channel", "out_pitch", "out_velocity",
        "out_onset_sec", "out_duration_sec", "out_new_channel", "out_new_program", "out_new_instrument"
    ]
    
    # Use the original note matrix (nmat_in) for the original DataFrame.
    import_df = pd.DataFrame(nmat_in, columns=columns_in)
    
    # Instead of using nmat_out (which has only 7 columns), we use our orchestrated DataFrame (df_orch)
    # because it still has our extra columns.
    export_df = df_orch.copy()
    # Rename its columns to match our desired naming convention:
    export_df.columns = columns_orch
    
    # To compare side-by-side, pad the original with empty columns for the extra fields.
    for col in columns_orch[7:]:
        import_df[col] = ""
    
    # Optionally, sort both DataFrames (if desired)
    import_df = import_df.sort_values(by=["in_onset_beats", "in_pitch"]).reset_index(drop=True)
    export_df = export_df.sort_values(by=["out_onset_beats", "out_pitch"]).reset_index(drop=True)
    
    max_len = max(len(import_df), len(export_df))
    import_df = import_df.reindex(range(max_len))
    export_df = export_df.reindex(range(max_len))
    blank_col = pd.DataFrame({"": [""] * max_len})
    comparison_df = pd.concat([import_df, blank_col, export_df], axis=1)
    comparison_df.to_excel(comparison_xlsx, index=False)
    
    print(f"Orchestrated roundtrip complete.\nNew MIDI written to {output_midi}\nComparison Excel saved as {comparison_xlsx}.")
    
    # 8. Evaluation (convert note matrices to simple note lists using onset_sec as start)
    def nmat_to_eval_list(nmat):
        note_list = []
        for row in nmat:
            note_list.append({
                "pitch": row[3],
                "start": row[5]
            })
        return note_list

    piano_notes = nmat_to_eval_list(nmat_in)
    # For evaluation of orchestration we use the original 7-column note matrix from the MIDI file.
    orchestration_notes = nmat_to_eval_list(nmat_out)
    
    eval_metrics = evaluate_orchestration(
        piano_notes, orchestration_notes, combo1_duration=16, combo2_duration=8
    )
    
    print("Evaluation Metrics:")
    for metric, value in eval_metrics.items():
        print(f"  {metric}: {value:.2f}")
    
    print("Additional Evaluation Metrics (for the original MIDI):")
    print("  Pitch Class Entropy:", pitch_class_entropy(input_midi))
    print("  Scale Consistency:", scale_consistency(input_midi))
    print("  Average Polyphony:", average_polyphony(input_midi))
    
    # 9. Visualization
    orig_notes_vis = nmat_to_note_list_vis(nmat_in)
    orch_notes_vis = nmat_to_note_list_vis(nmat_out)
    
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    plot_piano_roll(orig_notes_vis, title="Original Piano Roll", ax=axs[0, 0])
    plot_polyphony(orig_notes_vis, title="Original Polyphony", ax=axs[0, 1])
    plot_piano_roll(orch_notes_vis, title="Orchestrated Piano Roll", ax=axs[1, 0])
    plot_polyphony(orch_notes_vis, title="Orchestrated Polyphony", ax=axs[1, 1])
    plt.tight_layout()
    plt.show()
