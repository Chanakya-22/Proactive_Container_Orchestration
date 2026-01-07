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
        # If output is empty or fails, return 0.0
        if not stats_output:
            return 0.0
            
        cpu_val = float(stats_output.replace('%', ''))
        return cpu_val

    except Exception as e:
        # print(f"Debug: {e}") # Uncomment if you need to debug
        return 0.0

def log_metrics():
    print("DEBUG: Logger Started... (Press Ctrl+C to stop)")
    
    try:
        client = docker.from_env()
    except Exception as e:
        print(f"CRITICAL ERROR: Docker not connected. {e}")
        return

    print(f"Logging metrics for {SERVICE_NAME} to {LOG_FILE}...")
    
    # Overwrite old file with a fresh header
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time_Sec", "CPU_Percent", "Replicas"])
        
    start_time = time.time()
    
    try:
        while True:
            elapsed = int(time.time() - start_time)
            
            # 1. Get Replicas (Safe check)
            try:
                service = client.services.get(SERVICE_NAME)
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            except:
                replicas = 0

            # 2. Get CPU (Robust Method)
            cpu = get_cpu_robust(SERVICE_NAME)
            
            # 3. Save to CSV
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([elapsed, cpu, replicas])
                
            # Print status to terminal
            print(f"Sec: {elapsed} | CPU: {cpu:.1f}% | Replicas: {replicas}", end='\r')
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nLogging Stopped.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    log_metrics()