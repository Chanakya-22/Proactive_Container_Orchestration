import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import glob
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'universal_training_data.csv')

def process_universal_data():
    print("--- PHASE 1: UNIVERSAL DATA LOADER ---")
    
    # 1. Find all CSVs in data/raw
    all_files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    print(f"Found {len(all_files)} trace files. Merging for Generalization...")
    
    if len(all_files) == 0:
        print("ERROR: No CSV files found in data/raw/. Please add 5-10 Bitbrains files.")
        return

    combined_data = []

    # 2. Loop through every file and extract CPU usage
    for file in all_files:
        try:
            # Bitbrains uses semicolon ';' separators
            df = pd.read_csv(file, sep=';', engine='python')
            
            # Auto-detect CPU columns (Usage & Capacity)
            usage_col = next((c for c in df.columns if 'usage' in c and 'CPU' in c), None)
            cap_col = next((c for c in df.columns if 'capacity' in c and 'CPU' in c), None)
            
            if usage_col and cap_col:
                # Calculate Utilization %
                df['cpu_util'] = df[usage_col] / df[cap_col]
                
                # Clean Data (Remove infinity/NaN)
                df = df.replace([np.inf, -np.inf], np.nan).dropna()
                
                # Clip to 0.0 - 1.0 range
                df['cpu_util'] = df['cpu_util'].clip(0.0, 1.0)
                
                # Add to master list
                combined_data.append(df[['cpu_util']].values)
                print(f"   Loaded {os.path.basename(file)}: {len(df)} rows")
        except Exception as e:
            print(f"   Skipping {file}: {e}")

    # 3. Merge and Normalize
    if not combined_data:
        print("ERROR: No valid data extracted.")
        return

    full_dataset = np.vstack(combined_data)
    print(f"Total Universal Dataset: {len(full_dataset):,} rows.")
    
    # Normalize for LSTM
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(full_dataset)
    
    # 4. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    pd.DataFrame(scaled_data, columns=['cpu_scaled']).to_csv(OUTPUT_FILE, index=False)
    print(f"--- SUCCESS: Universal Data saved to {OUTPUT_FILE} ---")

if __name__ == '__main__':
    process_universal_data()