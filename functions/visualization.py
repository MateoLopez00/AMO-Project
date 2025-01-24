import matplotlib.pyplot as plt

# Plot the piano roll for visualization
def plot_piano_roll(notes, title="Piano Roll (Beats)"):
    """
    Plot the piano roll using beats instead of seconds.
    """
    plt.figure(figsize=(10, 6))
    for note in notes:
        plt.plot([note['start'], note['end']], [note['pitch'], note['pitch']], color='blue')
    plt.xlabel("Beats")
    plt.ylabel("Pitch")
    plt.title(title)
    plt.grid()
    plt.show()

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
