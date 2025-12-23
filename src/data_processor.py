import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'bitbrains.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'lstm_training_data.csv')

def process_bitbrains():
    print("--- DATA PROCESSING ---")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found.")
        return

    print("Loading data...")
    # Handle Bitbrains format
    try:
        df = pd.read_csv(INPUT_FILE, sep=';', engine='python')
    except:
        df = pd.read_csv(INPUT_FILE) # Fallback for standard CSV

    # Auto-detect CPU columns
    usage_col = next((c for c in df.columns if 'usage' in c and 'CPU' in c), None)
    cap_col = next((c for c in df.columns if 'capacity' in c and 'CPU' in c), None)

    if usage_col and cap_col:
        df['cpu_util'] = df[usage_col] / df[cap_col]
    else:
        # Fallback for generic CSVs
        df['cpu_util'] = df.iloc[:, 0] 

    # Clean and Normalize
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    df['cpu_util'] = df['cpu_util'].clip(0.0, 1.0)
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(df[['cpu_util']].values)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    pd.DataFrame(scaled, columns=['cpu_scaled']).to_csv(OUTPUT_FILE, index=False)
    print(f"Done. Saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    process_bitbrains()