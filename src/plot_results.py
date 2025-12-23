import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_comparison():
    # Look for files in the current folder (src)
    file_reactive = 'results_reactive.csv'
    file_proactive = 'results_proactive.csv'
    
    if not os.path.exists(file_reactive) or not os.path.exists(file_proactive):
        print("ERROR: Missing CSV files. Make sure you renamed 'experiment_results.csv' after each test.")
        return

    # Load data (header=None ensures we don't accidentally lose the first row if headers are missing)
    # We will try to load with headers first, if that fails, we load without.
    try:
        df_no_ai = pd.read_csv(file_reactive)
        if 'Time_Sec' not in df_no_ai.columns:
            # Reload without assuming a header exists
            df_no_ai = pd.read_csv(file_reactive, header=None)
            
        df_ai = pd.read_csv(file_proactive)
        if 'Time_Sec' not in df_ai.columns:
            df_ai = pd.read_csv(file_proactive, header=None)
            
    except Exception as e:
        print(f"Error reading CSVs: {e}")
        return

    plt.figure(figsize=(12, 8))

    # --- PLOT 1: CPU LOAD ---
    plt.subplot(2, 1, 1)
    # We use iloc[:, X] -> Get all rows for Column X
    # Column 0 = Time, Column 1 = CPU, Column 2 = Replicas
    
    plt.plot(df_no_ai.iloc[:, 0], df_no_ai.iloc[:, 1], 'r--', label='Without AI (Reactive)')
    plt.plot(df_ai.iloc[:, 0], df_ai.iloc[:, 1], 'g-', label='With AI (Proactive)')
    
    plt.title('Impact of AI on System Load')
    plt.ylabel('CPU Load (%)')
    plt.legend()
    plt.grid(True)

    # --- PLOT 2: SCALING (REPLICAS) ---
    plt.subplot(2, 1, 2)
    
    plt.plot(df_no_ai.iloc[:, 0], df_no_ai.iloc[:, 2], 'r--', label='Replicas (Reactive)')
    plt.plot(df_ai.iloc[:, 0], df_ai.iloc[:, 2], 'g-', linewidth=2, label='Replicas (AI Proactive)')
    
    plt.ylabel('Container Count')
    plt.xlabel('Time (Seconds)')
    plt.legend()
    plt.grid(True)

    output_path = 'final_comparison_graph.png'
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"SUCCESS: Graph saved as {output_path}")

if __name__ == "__main__":
    plot_comparison()