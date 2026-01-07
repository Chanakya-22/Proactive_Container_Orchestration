import time
import docker
import subprocess

SERVICE_NAME = "web_app"
UP_THRESHOLD = 80.0    # Scale UP if CPU > 80%
DOWN_THRESHOLD = 20.0  # Scale DOWN if CPU < 20%
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
        return float(stats_output.replace('%', ''))
    except:
        return 0.0

def start_reactive():
    print("--- REACTIVE AUTOSCALER (Standard Industry Logic) ---")
    client = docker.from_env()
    high_load_counter = 0  # To simulate "Reaction Lag"
    
    while True:
        try:
            cpu = get_cpu_robust(SERVICE_NAME)
            service = client.services.get(SERVICE_NAME)
            current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            
            print(f"Reactive Monitor | Load: {cpu:.1f}% | Replicas: {current_replicas} | Lag: {high_load_counter}/5s", end='\r')
            
            # LOGIC: Only scale if load is high for 5 consecutive seconds (Lag)
            if cpu > UP_THRESHOLD:
                high_load_counter += 1
            else:
                high_load_counter = 0
            
            # ACT
            if high_load_counter >= 5 and current_replicas < MAX_REPLICAS:
                print(f"\n[REACTIVE] Threshold breached for 5s! Scaling UP to {current_replicas + 1}...")
                service.scale(current_replicas + 1)
                high_load_counter = 0 # Reset
                time.sleep(5) # Cooldown
                
            elif cpu < DOWN_THRESHOLD and current_replicas > MIN_REPLICAS:
                print(f"\n[REACTIVE] Load low. Scaling DOWN to {current_replicas - 1}...")
                service.scale(current_replicas - 1)
                time.sleep(5)

            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            time.sleep(1)

if __name__ == "__main__":
    start_reactive()