import time
import numpy as np
import tensorflow as tf
from collections import deque
import os
import subprocess
import docker

# --- CONFIGURATION ---
SERVICE_NAME = "web_app"
# Auto-detect path to model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'orchestrator_brain.h5')

# Tuning Parameters
WINDOW_SIZE = 60       # Must match training window
PREDICTION_THRESHOLD = 0.30  # SENSITIVE: Scale up if >30% load predicted
SAFE_THRESHOLD = 0.10        # Scale down if <10% load predicted
MAX_REPLICAS = 10
MIN_REPLICAS = 1

def get_cpu_robust(service_name):
    """
    Forces a direct call to Docker CLI to get the accurate CPU %.
    Bypasses Python library issues on Windows/WSL.
    """
    try:
        # 1. Find the Container ID of the service
        # We use shell=True to run the command exactly like in terminal
        cmd_id = f"docker ps --filter label=com.docker.swarm.service.name={service_name} --format {{{{.ID}}}}"
        output = subprocess.check_output(cmd_id, shell=True).decode().strip()
        
        if not output:
            return 0.0
            
        # Take the first container found
        container_id = output.split('\n')[0]

        # 2. Get CPU stats (snapshot)
        cmd_stats = f"docker stats {container_id} --no-stream --format {{{{.CPUPerc}}}}"
        stats_output = subprocess.check_output(cmd_stats, shell=True).decode().strip()
        
        # Clean string: "5.55%" -> 5.55
        cpu_val = float(stats_output.replace('%', ''))
        
        # Normalize: AI expects 0.0 to 1.0 (e.g., 50% = 0.5)
        # If you have 4 cores, 100% means 1 core full. We treat 100% as 1.0 for simplicity.
        return cpu_val / 100.0

    except Exception as e:
        # print(f"Debug: {e}") # Uncomment if you need to debug
        return 0.0

def start_orchestration():
    print("--- PHASE 3: AI ORCHESTRATOR (ROBUST MODE) ---")
    print(f"Target Service: {SERVICE_NAME}")
    
    # 1. Connect to Docker Daemon (for scaling commands)
    client = docker.from_env()
    
    # 2. Load Brain
    print(f"Loading Model from {MODEL_PATH}...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
    except OSError:
        print("CRITICAL ERROR: Model not found. Run 'lstm_trainer.py' first.")
        return

    # 3. Buffer
    history = deque(maxlen=WINDOW_SIZE)
    print("Warming up buffer (Need 60 seconds of data)...")

    while True:
        try:
            # A. OBSERVE (Using Robust Method)
            current_cpu = get_cpu_robust(SERVICE_NAME)
            history.append(current_cpu)
            
            # Display Status
            bar = "|" * int(current_cpu * 20)
            print(f"Load: {current_cpu*100:5.2f}% [{bar:<20}] Buffer: {len(history)}/{WINDOW_SIZE}", end='\r')

            # B. PREDICT
            if len(history) == WINDOW_SIZE:
                # Prepare data [1, 60, 1]
                input_data = np.array(history).reshape(1, WINDOW_SIZE, 1)
                prediction = model.predict(input_data, verbose=0)[0][0]
                pred_pct = prediction * 100
                
                # Clean Output for Demo
                print(f"\n>> AI FORECAST: {pred_pct:.2f}% Load Expected.")

                # C. ACT
                service = client.services.get(SERVICE_NAME)
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']

                if prediction > PREDICTION_THRESHOLD and current_replicas < MAX_REPLICAS:
                    print(f"   [ALERT] Spike Predicted! Scaling UP to {current_replicas + 1}...")
                    service.scale(current_replicas + 1)
                    history.clear() # Reset buffer to avoid double-scaling instantly
                    
                elif prediction < SAFE_THRESHOLD and current_replicas > MIN_REPLICAS:
                    print(f"   [INFO] System Idle. Scaling DOWN to {current_replicas - 1}...")
                    service.scale(current_replicas - 1)
                else:
                    print("   [OK] Holding Steady.")
            
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopping.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_orchestration()