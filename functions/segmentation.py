# segmentation.py
def segment_layers(note_df):
    """
    Segments a note DataFrame (which must contain a 'pitch' column) into:
      - melody: notes with pitch > 60
      - harmony: notes with 50 <= pitch <= 60
      - rhythm:  notes with pitch < 50
    Returns three DataFrames: melody, harmony, rhythm.
    """
    melody = note_df[note_df['pitch'] > 60]
    harmony = note_df[(note_df['pitch'] >= 50) & (note_df['pitch'] <= 60)]
    rhythm  = note_df[note_df['pitch'] < 50]
    return melody, harmony, rhythm
