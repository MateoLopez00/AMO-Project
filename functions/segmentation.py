# Segmentation into melody, harmony, and rhythm
def segment_layers(note_array):

    melody = note_array[note_array['pitch'] > 60]
    harmony = note_array[(note_array['pitch'] >= 50) & (note_array['pitch'] <= 60)]
    rhythm  = note_array[note_array['pitch'] < 50]

    return melody, harmony, rhythm

