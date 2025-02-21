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
    # Use vectorized operations:
    times = np.unique(np.concatenate((notes['start'], notes['end'])))
    # For each time point, count how many notes are active using vectorized comparisons.
    polyphony = [np.sum((notes['start'] <= t) & (notes['end'] > t)) for t in times]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
        
    ax.plot(times, polyphony, label="Polyphony", color='green')
    ax.set_xlabel("Beats")
    ax.set_ylabel("Number of Notes")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    return ax
