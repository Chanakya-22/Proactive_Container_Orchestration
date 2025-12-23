import docker
import time
import csv
import os
import subprocess

# --- CONFIGURATION ---
SERVICE_NAME = "web_app"
# Saves to the 'src' folder by default (where the script is running)
LOG_FILE = "experiment_results.csv"

def get_cpu_robust(service_name):
    """ Same robust logic as Orchestrator """
    try:
        cmd_id = f"docker ps --filter label=com.docker.swarm.service.name={service_name} --format {{{{.ID}}}}"
        output = subprocess.check_output(cmd_id, shell=True).decode().strip()
        if not output: return 0.0
        container_id = output.split('\n')[0]
        cmd_stats = f"docker stats {container_id} --no-stream --format {{{{.CPUPerc}}}}"
        stats_output = subprocess.check_output(cmd_stats, shell=True).decode().strip()
        return float(stats_output.replace('%', ''))
    except:
        return 0.0

def log_metrics():
    print("DEBUG: Logger Started...")
    
    client = docker.from_env()
    print(f"Logging metrics for {SERVICE_NAME} to {LOG_FILE}...")
    
    # Overwrite old file
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time_Sec", "CPU_Percent", "Replicas"])
        
    start_time = time.time()
    
    try:
        while True:
            elapsed = int(time.time() - start_time)
            
            # 1. Get Replicas
            try:
                service = client.services.get(SERVICE_NAME)
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            except:
                replicas = 0

            # 2. Get CPU
            cpu = get_cpu_robust(SERVICE_NAME)
            
            # 3. Save
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([elapsed, cpu, replicas])
                
            print(f"Sec: {elapsed} | CPU: {cpu:.1f}% | Replicas: {replicas}", end='\r')
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nLogging Stopped.")

if __name__ == "__main__":
    log_metrics()