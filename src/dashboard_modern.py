from flask import Flask, render_template, jsonify
import pandas as pd
import os
import time

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('modern_dashboard.html')

@app.route('/api/data')
def get_data():
    data = {}
    
    # 1. Load System Telemetry
    if os.path.exists("system_metrics.csv"):
        try:
            sys_df = pd.read_csv("system_metrics.csv").tail(60)
            data['sys_time'] = sys_df['Time'].tolist()
            data['cpu'] = sys_df['CPU_Percent'].tolist()
            data['mem'] = sys_df['Memory_Percent'].tolist()
            data['net'] = sys_df['Network_RX_MB'].tolist()
            data['replicas'] = sys_df['Replicas'].tolist()
        except:
            pass
    
    # 2. Load Traffic Telemetry
    if os.path.exists("traffic_metrics.csv"):
        try:
            traf_df = pd.read_csv("traffic_metrics.csv").tail(60)
            data['latency'] = traf_df['Avg_Latency_ms'].tolist()
            data['tokens_lost'] = traf_df['Tokens_Lost'].tolist()
            data['throughput'] = traf_df['Throughput_RPS'].tolist()
        except:
            pass
        
    return jsonify(data)

if __name__ == '__main__':
    # Running on 0.0.0.0 to allow access from other devices if needed
    print("Dashboard live at http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')