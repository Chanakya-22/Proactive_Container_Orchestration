import docker
import time
import csv
import psutil
import subprocess

SERVICE_NAME = "web_app"
LOG_FILE = "live_metrics.csv"

def get_docker_cpu(service_name):
    """ Get Container CPU % """
    try:
        cmd_id = f"docker ps --filter label=com.docker.swarm.service.name={service_name} --format {{{{.ID}}}}"
        output = subprocess.check_output(cmd_id, shell=True).decode().strip()
        if not output: return 0.0
        container_id = output.split('\n')[0]
        cmd_stats = f"docker stats {container_id} --no-stream --format {{{{.CPUPerc}}}}"
        stats_output = subprocess.check_output(cmd_stats, shell=True).decode().strip()
        if not stats_output: return 0.0
        return float(stats_output.replace('%', ''))
    except:
        return 0.0

def log_metrics():
    print("--- SYSTEM OBSERVER STARTED ---")
    client = docker.from_env()
    
    # Write Header
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Container_CPU", "Replicas", "Host_CPU", "Host_RAM", "Context_Switches"])

    start_time = time.time()
    
    while True:
        try:
            elapsed = int(time.time() - start_time)
            
            # 1. Container Metrics
            try:
                service = client.services.get(SERVICE_NAME)
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            except:
                replicas = 0
            
            cont_cpu = get_docker_cpu(SERVICE_NAME)
            
            # 2. HOST OS Metrics (The "Real-World" OS part)
            host_cpu = psutil.cpu_percent()
            host_ram = psutil.virtual_memory().percent
            ctx_switches = psutil.cpu_stats().ctx_switches
            
            # 3. Save
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([elapsed, cont_cpu, replicas, host_cpu, host_ram, ctx_switches])
            
            print(f"Time: {elapsed}s | Docker CPU: {cont_cpu}% | Host CPU: {host_cpu}%", end='\r')
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            time.sleep(1)

if __name__ == "__main__":
    log_metrics()