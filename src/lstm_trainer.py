import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'lstm_training_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_FILE = os.path.join(MODEL_DIR, 'orchestrator_brain.h5')
GRAPH_FILE = os.path.join(MODEL_DIR, 'training_accuracy.png')

# --- HYPERPARAMETERS (Tuned for Legion 5i / Bitbrains) ---
WINDOW_SIZE = 60       # Look back 1 hour (assuming 1 min intervals)
PREDICT_HORIZON = 1    # Predict next step
EPOCHS = 30            # More epochs because data is complex
BATCH_SIZE = 128       # Larger batch size for your 14900HX/4060

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length - PREDICT_HORIZON):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length + PREDICT_HORIZON - 1]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def train_brain():
    print("--- PHASE 2: TRAINING (Bitbrains Deep Learning) ---")
    
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found. Run processor first.")
        return
    
    print("1. Loading Data...")
    df = pd.read_csv(INPUT_FILE)
    dataset = df.values
    
    print(f"   Loaded {len(dataset):,} rows. Creating Sequences...")
    X, y = create_sequences(dataset, WINDOW_SIZE)
    
    # Split Train/Val
    train_size = int(len(X) * 0.8)
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]
    
    print(f"   Training on {len(X_train):,} samples.")

    print("2. Building Model...")
    model = Sequential([
        # Layer 1
        LSTM(units=100, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        # Layer 2
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        # Output
        Dense(units=1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    print("3. Training (GPU Accelerated if available)...")
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_val, y_val),
        callbacks=[early_stop],
        verbose=1
    )
    
    print(f"4. Saving Model to {MODEL_FILE}...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(MODEL_FILE)
    
    # Graph
    plt.figure(figsize=(10,6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Bitbrains Model Convergence')
    plt.ylabel('MSE Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.savefig(GRAPH_FILE)
    print(f"   Graph saved to {GRAPH_FILE}")

if __name__ == '__main__':
    train_brain()