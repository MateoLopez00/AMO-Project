import matplotlib.pyplot as plt

def plot_piano_roll(notes, title="Piano Roll (Beats)", ax=None):
    # If no axis is provided, create a new one.
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot each note as a horizontal line from start to end at the note's pitch.
    for note in notes:
        ax.plot([note['start'], note['end']], [note['pitch'], note['pitch']], color='blue')
    
    ax.set_xlabel("Beats")
    ax.set_ylabel("Pitch")
    ax.set_title(title)
    ax.grid(True)
    
    return ax

# Plot polyphony over time
def plot_polyphony(notes, title="Polyphony Over Time (Beats)", ax=None):
    # Calculate the time points from note start and end times.
    times = sorted(set(note['start'] for note in notes) | set(note['end'] for note in notes))
    # Calculate polyphony at each time point.
    polyphony = [sum(1 for note in notes if note['start'] <= t < note['end']) for t in times]
    
    # If no axis is provided, create one.
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
        
    # Plot the polyphony curve.
    ax.plot(times, polyphony, label="Polyphony", color='green')
    ax.set_xlabel("Beats")
    ax.set_ylabel("Number of Notes")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    return ax
