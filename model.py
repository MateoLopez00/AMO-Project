from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, MultiHeadAttention, LayerNormalization, Add
from tensorflow.keras.optimizers import Adam

def build_transformer_model(seq_len, feature_dim, num_classes):
    """
    Builds a Transformer Encoder-Decoder model for orchestration prediction.
    
    Parameters:
        seq_len (int): Length of input sequences.
        feature_dim (int): Number of input features.
        num_classes (int): Number of output classes (e.g., instruments).

    Returns:
        Model: A compiled Keras model.
    """
    # Encoder
    encoder_inputs = Input(shape=(seq_len, feature_dim), name="encoder_inputs")
    x = MultiHeadAttention(num_heads=4, key_dim=64)(encoder_inputs, encoder_inputs)
    x = Add()([encoder_inputs, x])
    x = LayerNormalization()(x)
    x = Dense(128, activation='relu')(x)  # Project to 128 dimensions (encoder output)

    # Decoder
    decoder_inputs = Input(shape=(seq_len, feature_dim), name="decoder_inputs")
    y = Dense(128, activation='relu')(decoder_inputs)  # Project decoder inputs to 128 dimensions
    y = MultiHeadAttention(num_heads=4, key_dim=64)(y, x)  # Align dimensions
    y = Add()([y, x])
    y = LayerNormalization()(y)
    y = Dense(128, activation='relu')(y)
    y = Dense(num_classes, activation='softmax')(y)

    # Build and compile the model
    model = Model([encoder_inputs, decoder_inputs], y, name="transformer_model")
    model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    return model