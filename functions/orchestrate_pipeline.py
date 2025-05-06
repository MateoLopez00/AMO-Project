from midi_processing import read_midi_full
from orchestration import apply_orchestration, write_array_to_midi
from evaluation import evaluate_orchestration, pitch_class_entropy, scale_consistency, average_polyphony
import pandas as pd
import matplotlib.pyplot as plt
from visualization import nmat_to_note_list_vis, plot_piano_roll, plot_polyphony


def orchestrate_pipeline(input_midi, output_midi, comparison_xlsx="comparison.xlsx"):
    # 1. Read full MIDI and note matrix
    midi_data, nmat_in = read_midi_full(input_midi)

    # 2. Create DataFrame of original notes
    cols_in = [
        "onset_beats", "duration_beats", "channel", "pitch", "velocity",
        "onset_sec", "duration_sec", "onset_quarters", "duration_quarters"
    ]
    df_in = pd.DataFrame(nmat_in, columns=cols_in)

    # 3. Apply orchestration rules (adds new_channel, new_program, new_instrument)
    df_orch = apply_orchestration(df_in)

    # 4. Convert orchestrated DataFrame back to NumPy array
    nmat_orch = df_orch.to_numpy()

    # 5. Write orchestrated MIDI from array
    write_array_to_midi(nmat_orch, output_midi)
    print(f"Orchestrated MIDI written to {output_midi}")

    # 6. Read back the new MIDI for comparison
    _, nmat_out = read_midi_full(output_midi)

    # 7. Build side-by-side comparison and save to Excel
    cols_out = [
        "out_onset_beats", "out_duration_beats", "out_channel", "out_pitch", "out_velocity",
        "out_onset_sec", "out_duration_sec", "out_onset_quarters", "out_duration_quarters",
        "out_new_channel", "out_new_program", "out_new_instrument"
    ]
    import_df = pd.DataFrame(nmat_in, columns=[c.replace("out_","in_") for c in cols_out[:9]])
    for col in cols_out[9:]:
        import_df[col] = ""
    export_df = df_orch.copy()
    export_df.columns = cols_out

    import_df = import_df.sort_values(by=["in_onset_beats", "in_pitch"]).reset_index(drop=True)
    export_df = export_df.sort_values(by=["out_onset_beats", "out_pitch"]).reset_index(drop=True)

    max_len = max(len(import_df), len(export_df))
    import_df = import_df.reindex(range(max_len))
    export_df = export_df.reindex(range(max_len))
    blank = pd.DataFrame({"": [""] * max_len})
    comparison_df = pd.concat([import_df, blank, export_df], axis=1)
    comparison_df.to_excel(comparison_xlsx, index=False)
    print(f"Comparison Excel saved to {comparison_xlsx}")

    # 8. Evaluation metrics
    piano_notes = [{"pitch": r[3], "start": r[5]} for r in nmat_in]
    orch_notes  = [{"pitch": r[3], "start": r[5]} for r in nmat_out]
    metrics = evaluate_orchestration(piano_notes, orch_notes)
    print("Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    print(f"Pitch Class Entropy: {pitch_class_entropy(input_midi):.2f}")
    print(f"Scale Consistency:   {scale_consistency(input_midi):.2f}")
    print(f"Average Polyphony:   {average_polyphony(input_midi):.2f}")

    # 9. Visualization (optional)
    orig_vis = nmat_to_note_list_vis(nmat_in)
    orch_vis = nmat_to_note_list_vis(nmat_out)
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    plot_piano_roll(orig_vis, "Original Piano Roll", ax=axs[0, 0])
    plot_polyphony(orig_vis, "Original Polyphony", ax=axs[0, 1])
    plot_piano_roll(orch_vis, "Orchestrated Piano Roll", ax=axs[1, 0])
    plot_polyphony(orch_vis, "Orchestrated Polyphony", ax=axs[1, 1])
    plt.tight_layout()
    plt.show()
