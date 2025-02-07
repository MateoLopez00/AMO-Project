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
def plot_polyphony(orchestration_notes):
    """
    Plot the polyphony (number of active notes) over time using beats.
    """
    times = sorted(set(note['start'] for note in orchestration_notes) |
                   set(note['end'] for note in orchestration_notes))
    polyphony = [
        sum(1 for note in orchestration_notes if note['start'] <= t < note['end'])
        for t in times
    ]

    plt.figure(figsize=(10, 5))
    plt.plot(times, polyphony, label="Polyphony")
    plt.xlabel("Beats")
    plt.ylabel("Number of Notes")
    plt.title("Polyphony Over Time (Beats)")
    plt.legend()
    plt.grid()
    plt.show()
