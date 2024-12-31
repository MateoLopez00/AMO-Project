import matplotlib.pyplot as plt

# Plot the piano roll for visualization
def plot_piano_roll(notes, title="Piano Roll"):
    """
    Plot the piano roll for visualization.
    """
    plt.figure(figsize=(10, 6))
    for note in notes:
        plt.plot([note['start'], note['end']], [note['pitch'], note['pitch']], color='blue')
    plt.xlabel("Time (s)")
    plt.ylabel("Pitch")
    plt.title(title)
    plt.grid()
    plt.show()

# Plot polyphony over time
def plot_polyphony(orchestration_notes):
    """
    Plot the polyphony (number of active notes) over time.
    """
    times = sorted(set(note['start'] for note in orchestration_notes) |
                   set(note['end'] for note in orchestration_notes))
    polyphony = [
        sum(1 for note in orchestration_notes if note['start'] <= t < note['end'])
        for t in times
    ]

    plt.figure(figsize=(10, 5))
    plt.plot(times, polyphony, label="Polyphony")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of Notes")
    plt.title("Polyphony Over Time")
    plt.legend()
    plt.grid()
    plt.show()
