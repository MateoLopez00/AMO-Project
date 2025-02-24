import sys
from mido import MidiFile, MidiTrack, Message, MetaMessage
from sklearn.cluster import KMeans
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# If you know the instrument ranges, you could define them here (MIDI note numbers):
# These ranges are just examples and may need adjustment.
instrument_setup = {
    "Violin 1":  {"range": (55, 103), "program": 40},  # GM: Violin
    "Violin 2":  {"range": (55, 91),  "program": 40},  # also a Violin
    "Viola":     {"range": (48, 76),  "program": 41},  # GM: Viola
    "Bass":      {"range": (28, 62),  "program": 33},  # GM: Acoustic Bass
    "Trumpet":   {"range": (54, 98),  "program": 57},  # GM: Trumpet
}

# Channels mapping: each instrument gets a channel
instruments = list(instrument_setup.keys())
instrument_channels = {inst: i for i, inst in enumerate(instruments)}

# Number of clusters = number of instruments
n_clusters = len(instruments)

# ---------------------------------------------------------------------------
# Input/Output Files
# ---------------------------------------------------------------------------

# if len(sys.argv) < 3:
#     print("Usage: python script.py input.mid output.mid")
#     sys.exit(1)

input_file = "examples/sugar-plum-fairy-piano_solo.mid"#sys.argv[1]
output_file = "output.mid"

# ---------------------------------------------------------------------------
# Read MIDI and Extract Notes
# ---------------------------------------------------------------------------

mid = MidiFile(input_file)
notes = []  # Will store (pitch, start_time, velocity, end_time)
notes_active = {}  # For tracking ongoing notes: key = pitch, value = (start_time, velocity, channel)

# Collect all messages with absolute times
all_msgs = []
for track in mid.tracks:
    absolute_time = 0
    for msg in track:
        absolute_time += msg.time
        all_msgs.append((absolute_time, msg))

# Sort all messages by absolute time
all_msgs.sort(key=lambda x: x[0])

# Separate meta messages and note messages
meta_msgs = []
note_msgs = []
for current_time, msg in all_msgs:
    if msg.is_meta:
        meta_msgs.append((current_time, msg))
    else:
        note_msgs.append((current_time, msg))

# Process note messages
notes = []
notes_active = {}
for current_time, msg in note_msgs:
    if msg.type == 'note_on' and msg.velocity > 0:
        notes_active[(msg.note, msg.channel)] = (current_time, msg.velocity, msg.channel)
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        key_candidates = [(msg.note, c) for c in range(16)]
        key_found = None
        for k in key_candidates:
            if k in notes_active:
                key_found = k
                break
        if key_found is not None:
            start_time, velocity, ch = notes_active.pop(key_found)
            notes.append((msg.note, start_time, velocity, current_time))

# Convert to numpy array for clustering: we only need pitch for k-means
pitches = np.array([n[0] for n in notes]).reshape(-1, 1)

# ---------------------------------------------------------------------------
# Perform K-Means Clustering
# ---------------------------------------------------------------------------

kmeans = KMeans(n_clusters=n_clusters, random_state=42)
clusters = kmeans.fit_predict(pitches)

# Create mapping from cluster labels to instruments
cluster_to_instrument = {i: inst for i, inst in enumerate(instruments)}

# Combine notes and their cluster labels
notes_with_clusters = list(zip(notes, clusters))

# Sort notes by start time
notes_with_clusters.sort(key=lambda x: x[0][1])

# After sorting, create events
events = []
for (note, start, velocity, end), cluster_label in notes_with_clusters:
    inst = cluster_to_instrument[cluster_label]
    ch = instrument_channels[inst]
    # Note on event
    events.append({'type': 'note_on', 'time': start, 'note': note, 'velocity': velocity, 'channel': ch})
    # Note off event
    events.append({'type': 'note_off', 'time': end, 'note': note, 'velocity': 0, 'channel': ch})

# ---------------------------------------------------------------------------
# Write Out the New MIDI File
# ---------------------------------------------------------------------------

# Create a new MIDI file with same structure
out_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)

# Copy all tracks
for track_idx, track in enumerate(mid.tracks):
    out_track = MidiTrack()
    out_mid.tracks.append(out_track)
    
    # Add program changes at the start of the first track
    if track_idx == 0:
        for inst, ch in instrument_channels.items():
            program_number = instrument_setup[inst]["program"]
            out_track.append(Message('program_change', program=program_number, channel=ch, time=0))
    
    current_notes = {}  # Keep track of active notes for clustering
    
    for msg in track:
        if msg.type in ['note_on', 'note_off']:
            # Find cluster for this note
            cluster_label = kmeans.predict([[msg.note]])[0]
            inst = cluster_to_instrument[cluster_label]
            new_channel = instrument_channels[inst]
            
            # Copy message with new channel
            new_msg = msg.copy(channel=new_channel)
            out_track.append(new_msg)
        else:
            # Copy all other messages as-is
            out_track.append(msg.copy())

out_mid.save(output_file)

print(f"Orchestral MIDI file written to {output_file}")