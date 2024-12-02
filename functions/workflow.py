import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from model import build_transformer_model
from midi_processing import midi_to_nmat
from data_processing import pad_features, split_into_chunks
from evaluation import evaluate_predictions
from save_midi import save_predictions_to_midi

def main_workflow(piano_file, orchestra_file, seq_len=50, feature_dim=6):
    # Convert MIDI to Note Matrices
    piano_nmat = midi_to_nmat(piano_file)
    orchestra_nmat = midi_to_nmat(orchestra_file)

    # Normalize features
    scaler = MinMaxScaler()
    piano_features = scaler.fit_transform(piano_nmat[:, :feature_dim])
    orchestra_labels = orchestra_nmat[:, 2].astype(int)  # Use instrument programs as labels

    # Split into chunks
    piano_chunks, label_chunks = split_into_chunks(piano_features, orchestra_labels, seq_len)

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(piano_chunks, label_chunks, test_size=0.2, random_state=42)

    # One-hot encode labels
    num_classes = 128
    y_train_onehot = np.zeros((len(y_train), seq_len, num_classes))
    y_test_onehot = np.zeros((len(y_test), seq_len, num_classes))
    for i, chunk in enumerate(y_train):
        for j, label in enumerate(chunk):
            y_train_onehot[i, j, label] = 1
    for i, chunk in enumerate(y_test):
        for j, label in enumerate(chunk):
            y_test_onehot[i, j, label] = 1

    # Build and train the model
    model = build_transformer_model(seq_len, feature_dim, num_classes)
    model.fit([X_train, X_train], y_train_onehot, epochs=20, batch_size=16, verbose=0)

    # Predict on the test set
    predictions = model.predict([X_test, X_test], verbose=0)
    y_pred = np.argmax(predictions, axis=-1).flatten()
    y_true = y_test.flatten()

    # Save predictions as a MIDI file
    save_predictions_to_midi(y_pred, "./predicted_orchestral_output.mid", seq_len, feature_dim)

    # Evaluate predictions
    precision, recall = evaluate_predictions(y_true, y_pred)
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
