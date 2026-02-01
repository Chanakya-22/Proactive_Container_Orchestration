from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')

# This monitors the SAME file that logger.py writes to
LOG_FILE = "live_metrics.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    if not os.path.exists(LOG_FILE):
        return jsonify({'time': [], 'cpu': [], 'replicas': [], 'status': 'WAITING FOR DATA...'})
    
    try:
        # Read only the last 50 rows for the "Heartbeat" effect
        df = pd.read_csv(LOG_FILE).tail(50)
        
        # Calculate Proactiveness: Are we safe?
        # Safe = Replicas > 1 AND CPU is not crazy high (avoiding the crash)
        current_cpu = df['Container_CPU'].iloc[-1]
        current_replicas = df['Replicas'].iloc[-1]
        
        status = "MONITORING"
        if current_replicas > 1:
            status = "PROACTIVE DEFENSE ACTIVE"
        if current_cpu > 150:
            status = "SYSTEM CRITICAL (REACTIVE FAIL)"

        data = {
            'time': df['Time'].tolist(),
            'cpu': df['Container_CPU'].tolist(),
            'replicas': df['Replicas'].tolist(),
            'host_cpu': df['Host_CPU'].tolist() if 'Host_CPU' in df else [],
            'status': status
        }
        return jsonify(data)
    except Exception as e:
        print(f"Error reading data: {e}")
        return jsonify({'time': [], 'cpu': [], 'status': 'ERROR'})

if __name__ == '__main__':
    print("Starting Dashboard on http://localhost:5000")
    app.run(debug=True, port=5000)