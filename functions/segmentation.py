# Segmentation into melody, harmony, and rhythm
def segment_layers(notes):
    """
    Segment notes into melody, harmony, and rhythm layers.
    """
    melody = [note for note in notes if note['pitch'] > 60]
    harmony = [note for note in notes if 50 <= note['pitch'] <= 60]
    rhythm = [note for note in notes if note['pitch'] < 50]

    return melody, harmony, rhythm
