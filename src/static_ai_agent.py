import time
import numpy as np
import tensorflow as tf
from collections import deque
import docker
import os
import subprocess

# Config
SERVICE_NAME = "web_app"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'orchestrator_brain.h5')
WINDOW_SIZE = 60
FIXED_THRESHOLD = 0.50  # Dumb, fixed threshold

# (Insert get_cpu_robust function here or import it)
def get_cpu_robust(service_name):
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

def start_static_ai():
    print("--- STATIC AI AGENT (Competitor) ---")
    client = docker.from_env()
    model = tf.keras.models.load_model(MODEL_PATH)
    history = deque(maxlen=WINDOW_SIZE)
    
    print("Warming up buffer...")
    while True:
        try:
            current_cpu = get_cpu_robust(SERVICE_NAME)
            history.append(current_cpu)
            
            if len(history) == WINDOW_SIZE:
                input_data = np.array(history).reshape(1, WINDOW_SIZE, 1)
                prediction = model.predict(input_data, verbose=0)[0][0]
                
                service = client.services.get(SERVICE_NAME)
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                
                # RIGID LOGIC: Only scale if > 50%. No adaptation.
                if prediction > FIXED_THRESHOLD and current_replicas < 10:
                    print(f"[STATIC] Pred {prediction:.2f} > 0.50. Scaling UP.")
                    service.scale(current_replicas + 1)
                    history.clear()
                elif prediction < 0.20 and current_replicas > 1:
                    service.scale(current_replicas - 1)
            
            time.sleep(1)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    start_static_ai()