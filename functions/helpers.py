def nmat_to_note_list(nmat):
    """
    Converts a note matrix (assumed to have columns:
    [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec])
    into a list of dictionaries with keys "pitch" and "start".
    We use onset_sec (column index 5) as the note's start time.
    """
    note_list = []
    for row in nmat:
        start_time = row[5] if len(row) >= 7 else row[0]
        note_list.append({
            "pitch": row[3],
            "start": start_time
        })
    return note_list
