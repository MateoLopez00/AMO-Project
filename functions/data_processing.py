import numpy as np

def pad_features(features, seq_len, feature_dim):
    padded = np.zeros((seq_len, feature_dim))
    num_samples = min(seq_len, features.shape[0])
    padded[:num_samples] = features[:num_samples]
    return padded

def split_into_chunks(features, labels, seq_len):
    num_chunks = len(features) // seq_len
    feature_chunks = [features[i * seq_len:(i + 1) * seq_len] for i in range(num_chunks)]
    label_chunks = [labels[i * seq_len:(i + 1) * seq_len] for i in range(num_chunks)]
    return np.array(feature_chunks), np.array(label_chunks)