import numpy as np
import matplotlib.pyplot as plt

def plot_piano_roll(notes, title="Piano Roll (Beats)", ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Looping is fine here; each element is still accessed by field name.
    for note in notes:
        ax.plot([note['start'], note['end']], [note['pitch'], note['pitch']], color='blue')
    
    ax.set_xlabel("Beats")
    ax.set_ylabel("Pitch")
    ax.set_title(title)
    ax.grid(True)
    return ax

def plot_polyphony(notes, title="Polyphony Over Time (Beats)", ax=None):
    # Check if notes is a list of dicts
    if isinstance(notes, list):
        start_vals = np.array([note['start'] for note in notes])
        end_vals = np.array([note['end'] for note in notes])
    else:
        # Assume notes is a structured array with 'start' and 'end' fields.
        start_vals = notes['start']
        end_vals = notes['end']
    
    # Use vectorized operations to get unique time points.
    times = np.unique(np.concatenate((start_vals, end_vals)))
    # For each time point, count how many notes are active.
    polyphony = [np.sum((start_vals <= t) & (end_vals > t)) for t in times]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
        
    ax.plot(times, polyphony, label="Polyphony", color='green')
    ax.set_xlabel("Beats")
    ax.set_ylabel("Number of Notes")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    return ax
