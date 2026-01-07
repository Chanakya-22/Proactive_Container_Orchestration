import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_comparison():
    file_reactive = 'results_reactive.csv'
    file_proactive = 'results_proactive.csv'
    
    if not os.path.exists(file_reactive) or not os.path.exists(file_proactive):
        print("ERROR: Missing CSV files.")
        return

    # Load data (Header-safe)
    try:
        df_no_ai = pd.read_csv(file_reactive)
        if 'Time_Sec' not in df_no_ai.columns: df_no_ai = pd.read_csv(file_reactive, header=None)
            
        df_ai = pd.read_csv(file_proactive)
        if 'Time_Sec' not in df_ai.columns: df_ai = pd.read_csv(file_proactive, header=None)
    except Exception as e:
        print(f"Error: {e}")
        return

    plt.figure(figsize=(12, 8))

    # CPU Load Comparison
    plt.subplot(2, 1, 1)
    plt.plot(df_no_ai.iloc[:, 0], df_no_ai.iloc[:, 1], 'r--', label='Reactive (Standard)')
    plt.plot(df_ai.iloc[:, 0], df_ai.iloc[:, 1], 'g-', label='Proactive (Adaptive AI)')
    plt.title('Impact of Adaptive AI on System Load')
    plt.ylabel('CPU Load (%)')
    plt.legend()
    plt.grid(True)

    # Scaling Action Comparison
    plt.subplot(2, 1, 2)
    plt.plot(df_no_ai.iloc[:, 0], df_no_ai.iloc[:, 2], 'r--', label='Replicas (Reactive)')
    plt.plot(df_ai.iloc[:, 0], df_ai.iloc[:, 2], 'g-', linewidth=2, label='Replicas (Adaptive AI)')
    plt.ylabel('Container Count')
    plt.xlabel('Time (Seconds)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('final_comparison_graph.png')
    print("Graph saved as final_comparison_graph.png")

if __name__ == "__main__":
    plot_comparison()