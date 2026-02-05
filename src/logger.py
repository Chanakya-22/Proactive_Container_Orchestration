import docker
import time
import csv
import psutil
import os

SERVICE_NAME = "web_app"
LOG_FILE = "system_metrics.csv"

def log_metrics():
    print("--- 🛰️ SYSTEM TELEMETRY STARTED ---")
    client = docker.from_env()
    
    # Write Header (The 7 Attributes)
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "CPU_Percent", "Memory_Percent", "Network_RX_MB", "Disk_Usage_Percent", "Context_Switches", "Replicas"])
        
    start_time = time.time()
    net_io_start = psutil.net_io_counters()
    
    while True:
        elapsed = int(time.time() - start_time)
        try:
            # 1. Container Replicas
            try:
                service = client.services.get(SERVICE_NAME)
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            except:
                replicas = 0
            
            # 2. Host Metrics (CPU, RAM, Disk)
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # 3. Network I/O (Delta)
            net_io_now = psutil.net_io_counters()
            net_rx_mb = (net_io_now.bytes_recv - net_io_start.bytes_recv) / 1024 / 1024
            
            # 4. Kernel Context Switches (OS Stress)
            ctx_switches = psutil.cpu_stats().ctx_switches
            
            # Save
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([elapsed, cpu, mem, round(net_rx_mb, 2), disk, ctx_switches, replicas])
                
            print(f"Sec: {elapsed} | CPU: {cpu}% | RAM: {mem}% | Replicas: {replicas}", end='\r')
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    log_metrics()