import requests
import time
import csv
import random
import argparse
import concurrent.futures

# Configuration
URL = "http://localhost:8080"
LOG_FILE = "traffic_metrics.csv"
THREADS = 10  # Utilizing your i9 processor

def send_request(session, request_id):
    """Sends a single request and returns metrics."""
    start = time.time()
    try:
        # Randomize "Heavy" vs "Light" requests
        if random.random() > 0.8:
            # Simulate heavy computation/database
            resp = session.get(URL, params={'type': 'heavy'}, timeout=5)
        else:
            resp = session.get(URL, timeout=5)
            
        latency = (time.time() - start) * 1000  # ms
        return latency, resp.status_code
    except Exception:
        # Network Timeout or Connection Refused
        return 5000, 503

def start_traffic(duration=120):
    print(f"--- 🚀 HIGH-LOAD TRAFFIC BOT STARTED ({THREADS} Threads) ---")
    
    # Initialize Log
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Avg_Latency_ms", "Throughput_RPS", "Tokens_Lost", "Success_Rate"])

    start_time = time.time()
    session = requests.Session()
    
    while True:
        cycle_start = time.time()
        elapsed = int(cycle_start - start_time)
        if elapsed > duration:
            break

        # Launch parallel requests
        latencies = []
        statuses = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = [executor.submit(send_request, session, i) for i in range(THREADS)]
            for future in concurrent.futures.as_completed(futures):
                lat, code = future.result()
                latencies.append(lat)
                statuses.append(code)

        # Calculate "Journal-Grade" Metrics
        avg_latency = sum(latencies) / len(latencies)
        throughput = len(latencies) / (time.time() - cycle_start)
        
        # Definition of "Token Lost": Status != 200 OR Latency > 2000ms
        tokens_lost = sum(1 for i in range(len(latencies)) if statuses[i] != 200 or latencies[i] > 2000)
        success_rate = ((THREADS - tokens_lost) / THREADS) * 100

        # Log Data
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([elapsed, round(avg_latency, 2), round(throughput, 1), tokens_lost, round(success_rate, 1)])
            
        print(f"Sec: {elapsed} | Lat: {avg_latency:.0f}ms | Lost: {tokens_lost} | RPS: {throughput:.1f}", end='\r')
        
        # Dynamic Sleep to prevent self-DDoS (keeping it realistic)
        time.sleep(0.5)

if __name__ == "__main__":
    start_traffic(duration=300) # Runs for 5 minutes