import time
import numpy as np
import tensorflow as tf
from collections import deque
import os
import subprocess
import docker

# --- CONFIGURATION ---
SERVICE_NAME = "web_app"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'orchestrator_brain.h5')

WINDOW_SIZE = 60
MAX_REPLICAS = 10
MIN_REPLICAS = 1

def get_cpu_robust(service_name):
    """ Direct Docker CLI check """
    try:
        cmd_id = f"docker ps --filter label=com.docker.swarm.service.name={service_name} --format {{{{.ID}}}}"
        output = subprocess.check_output(cmd_id, shell=True).decode().strip()
        if not output: return 0.0
        container_id = output.split('\n')[0]
        cmd_stats = f"docker stats {container_id} --no-stream --format {{{{.CPUPerc}}}}"
        stats_output = subprocess.check_output(cmd_stats, shell=True).decode().strip()
        return float(stats_output.replace('%', '')) / 100.0
    except:
        return 0.0

def start_orchestration():
    print("--- PHASE 3: ADAPTIVE AI ORCHESTRATOR ---")
    client = docker.from_env()
    print(f"Loading Universal Model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    
    history = deque(maxlen=WINDOW_SIZE)
    print("Warming up buffer (Need 60 seconds)...")

    while True:
        try:
            # A. OBSERVE
            current_cpu = get_cpu_robust(SERVICE_NAME)
            history.append(current_cpu)
            
            # NOVELTY: Calculate Volatility (Standard Deviation)
            # If traffic is unstable (High Std Dev), we lower the threshold to be safer.
            volatility = np.std(history) if len(history) > 1 else 0.0
            
            # Dynamic Threshold Formula
            # Base = 0.60 (60%). Subtract volatility.
            # Example: If volatility is 0.1, Threshold becomes 0.40 (40%).
            dynamic_threshold = 0.60 - (volatility * 2.0)
            dynamic_threshold = max(0.20, min(dynamic_threshold, 0.80)) # Clamp between 20% and 80%
            
            print(f"Load: {current_cpu*100:5.1f}% | Volatility: {volatility:.3f} | Dynamic Thresh: {dynamic_threshold*100:.1f}%", end='\r')

            # B. PREDICT
            if len(history) == WINDOW_SIZE:
                input_data = np.array(history).reshape(1, WINDOW_SIZE, 1)
                prediction = model.predict(input_data, verbose=0)[0][0]
                
                # C. ACT (Using DYNAMIC Threshold)
                service = client.services.get(SERVICE_NAME)
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']

                if prediction > dynamic_threshold and current_replicas < MAX_REPLICAS:
                    print(f"\n   [ADAPTIVE ALERT] Spike {prediction*100:.1f}% > Thresh {dynamic_threshold*100:.1f}%! Scaling UP...")
                    service.scale(current_replicas + 1)
                    history.clear() # Reset buffer
                    
                elif prediction < 0.10 and current_replicas > MIN_REPLICAS:
                    print(f"\n   [INFO] System Idle. Scaling DOWN...")
                    service.scale(current_replicas - 1)
            
            time.sleep(1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_orchestration()