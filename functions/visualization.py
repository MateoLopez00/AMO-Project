import numpy as np
import matplotlib.pyplot as plt

def nmat_to_note_list_vis(nmat):
    """
    Convert a note matrix (nmat) to a list of dictionaries for visualization.
    Assumes nmat has columns:
      [onset_beats, duration_beats, channel, pitch, velocity, onset_sec, duration_sec]
    We use onset_sec as the start time and compute the end time as onset_sec + duration_sec.
    """
    note_list = []
    for row in nmat:
        note_dict = {
            "start": row[5],
            "end": row[5] + row[6],
            "pitch": row[3]
        }
        note_list.append(note_dict)
    return note_list

def plot_piano_roll(notes, title="Piano Roll", ax=None):
    """
    Plot a piano roll from a list of note dictionaries.
    Each note is plotted as a horizontal line from its start to end time at its pitch.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    for note in notes:
        ax.plot([note['start'], note['end']], [note['pitch'], note['pitch']], color='blue')
    
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Pitch")
    ax.set_title(title)
    ax.grid(True)
    return ax

def plot_polyphony(notes, title="Polyphony Over Time", ax=None):
    """
    Plot the number of simultaneous notes (polyphony) over time.
    """
    # Extract start and end times
    start_vals = np.array([note['start'] for note in notes])
    end_vals = np.array([note['end'] for note in notes])
    
    # Get unique time points (all start and end times)
    times = np.unique(np.concatenate((start_vals, end_vals)))
    # For each time point, count the number of active notes.
    polyphony = [np.sum((start_vals <= t) & (end_vals > t)) for t in times]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
        
    ax.plot(times, polyphony, label="Polyphony", color='green')
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Number of Notes")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    return ax
