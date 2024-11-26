import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from model import build_transformer_model
from midi_processing import midi_to_nmat
from data_processing import pad_features, split_into_chunks
from evaluation import evaluate_predictions

def main_workflow(piano_file, orchestra_file, seq_len=50, feature_dim=6):
    """
    Main workflow for converting piano MIDI to orchestral MIDI using a Transformer model.
    
    Parameters:
        piano_file (str): Path to the piano MIDI file.
        orchestra_file (str): Path to the orchestral MIDI file.
        seq_len (int): Length of input sequences.
        feature_dim (int): Number of input features.
    
    Prints:
        Precision and recall scores.
    """
    # Step 1: Convert MIDI to Note Matrices
    piano_nmat = midi_to_nmat(piano_file)
    orchestra_nmat = midi_to_nmat(orchestra_file)

    # Step 2: Normalize features
    scaler = MinMaxScaler()
    piano_features = scaler.fit_transform(piano_nmat[:, :feature_dim])
    orchestra_labels = orchestra_nmat[:, 2].astype(int)  # Use instrument channels as labels

    # Step 3: Split into chunks
    piano_chunks, label_chunks = split_into_chunks(piano_features, orchestra_labels, seq_len)

    # Step 4: Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(piano_chunks, label_chunks, test_size=0.2, random_state=42)

    # Step 5: One-hot encode labels
    num_classes = 128
    y_train_onehot = np.zeros((len(y_train), seq_len, num_classes))
    y_test_onehot = np.zeros((len(y_test), seq_len, num_classes))
    for i, chunk in enumerate(y_train):
        for j, label in enumerate(chunk):
            y_train_onehot[i, j, label] = 1
    for i, chunk in enumerate(y_test):
        for j, label in enumerate(chunk):
            y_test_onehot[i, j, label] = 1

    # Step 6: Build and train the model
    model = build_transformer_model(seq_len, feature_dim, num_classes)
    model.fit([X_train, X_train], y_train_onehot, epochs=20, batch_size=16, verbose=1)

    # Step 7: Predict on the test set
    predictions = model.predict([X_test, X_test], verbose=1)
    y_pred = np.argmax(predictions, axis=-1).flatten()
    y_true = y_test.flatten()

    # Step 8: Evaluate predictions
    precision, recall = evaluate_predictions(y_true, y_pred)
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")