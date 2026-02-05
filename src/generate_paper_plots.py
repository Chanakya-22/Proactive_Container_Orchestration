import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration for Journal Quality
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
OUTPUT_DIR = "paper_assets"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_plots():
    print("--- Generating Journal Figures ---")
    
    # 1. Load Data
    try:
        sys_df = pd.read_csv("system_metrics.csv")
        traf_df = pd.read_csv("traffic_metrics.csv")
    except FileNotFoundError:
        print("ERROR: CSV files not found. Run the experiment first!")
        return

    # Ensure datasets align (roughly) by index or time if needed
    # For this script, we assume they ran concurrently
    limit = min(len(sys_df), len(traf_df))
    sys_df = sys_df.iloc[:limit]
    traf_df = traf_df.iloc[:limit]

    # --- FIGURE 1: Latency vs CPU Correlation (The Core Problem) ---
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('CPU Load (%)', color='tab:blue')
    ax1.plot(sys_df['Time'], sys_df['CPU_Percent'], color='tab:blue', label='CPU Load')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Latency (ms)', color='tab:red')
    ax2.plot(traf_df['Time'], traf_df['Avg_Latency_ms'], color='tab:red', linestyle='--', label='Latency')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    
    plt.title("Fig 1. Correlation between CPU Saturation and Service Latency")
    fig.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/Fig1_Latency_CPU.png", dpi=300)
    print("Saved Fig 1.")

    # --- FIGURE 2: Throughput vs Scaling (The Solution) ---
    plt.figure(figsize=(10, 6))
    plt.plot(traf_df['Time'], traf_df['Throughput_RPS'], label='Throughput (Req/s)', color='green')
    plt.fill_between(sys_df['Time'], sys_df['Replicas'] * 10, color='cyan', alpha=0.2, label='Active Replicas (Scaled x10)')
    plt.ylabel("Requests Per Second")
    plt.xlabel("Time (s)")
    plt.title("Fig 2. System Throughput Maintenance during Scaling Events")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/Fig2_Throughput_Scaling.png", dpi=300)
    print("Saved Fig 2.")

    # --- FIGURE 3: Tokens Lost Analysis (Reliability) ---
    plt.figure(figsize=(10, 6))
    plt.bar(traf_df['Time'], traf_df['Tokens_Lost'], color='orange', label='Failed Requests (Tokens Lost)')
    plt.plot(sys_df['Time'], sys_df['CPU_Percent'], color='black', alpha=0.3, label='System Load Overlay')
    plt.xlabel("Time (s)")
    plt.ylabel("Count")
    plt.title("Fig 3. Temporal Distribution of Token Loss during High Load")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/Fig3_Token_Loss.png", dpi=300)
    print("Saved Fig 3.")

    # --- FIGURE 4: Resource Overhead (Network & Memory) ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.stackplot(sys_df['Time'], sys_df['Memory_Percent'], sys_df['Network_RX_MB'], 
                 labels=['Memory Usage (%)', 'Network RX (MB)'], colors=['purple', 'gray'])
    plt.legend(loc='upper left')
    plt.title("Fig 4. Resource Overhead Profile (Memory & Network)")
    plt.savefig(f"{OUTPUT_DIR}/Fig4_Resource_Overhead.png", dpi=300)
    print("Saved Fig 4.")

    # --- TABLE 1: Statistical Summary CSV ---
    summary = {
        "Metric": ["Avg Latency", "Max CPU", "Total Tokens Lost", "Avg Throughput", "Max Replicas"],
        "Value": [
            f"{traf_df['Avg_Latency_ms'].mean():.2f} ms",
            f"{sys_df['CPU_Percent'].max():.2f} %",
            f"{traf_df['Tokens_Lost'].sum()}",
            f"{traf_df['Throughput_RPS'].mean():.2f} req/s",
            f"{sys_df['Replicas'].max()}"
        ]
    }
    pd.DataFrame(summary).to_csv(f"{OUTPUT_DIR}/Table1_Performance_Summary.csv", index=False)
    print("Saved Table 1.")

if __name__ == "__main__":
    generate_plots()