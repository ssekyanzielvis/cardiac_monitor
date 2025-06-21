from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# In-memory storage for cardiac data
cardiac_data = {
    "latest_reading": {
        "hr": None,
        "spo2": None,
        "timestamp": None
    }
}

# Route to receive and store cardiac data
@app.route('/api/cardiac_data', methods=['POST'])
def receive_cardiac_data():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    hr = data.get('hr')
    spo2 = data.get('spo2')

    if hr is None or spo2 is None:
        return jsonify({'error': 'Missing hr or spo2 data'}), 400

    try:
        # Store the data in memory
        cardiac_data["latest_reading"] = {
            "hr": hr,
            "spo2": spo2,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return jsonify({'error': 'Failed to store data', 'details': str(e)}), 500

    return jsonify({
        'message': 'Data stored successfully',
        'hr': hr,
        'spo2': spo2,
        'timestamp': cardiac_data["latest_reading"]["timestamp"]
    }), 200

# Route to get latest reading
@app.route('/api/latest_reading', methods=['GET'])
def get_latest_reading():
    latest = cardiac_data["latest_reading"]
    if latest["hr"] is not None and latest["spo2"] is not None:
        return jsonify({
            'hr': latest["hr"],
            'spo2': latest["spo2"],
            'timestamp': latest["timestamp"]
        })
    return jsonify({'error': 'No data available'}), 404

# Route to render the monitor template
@app.route('/')
def monitor():
    latest = cardiac_data["latest_reading"]
    hr = latest["hr"] if latest["hr"] is not None else 0
    spo2 = latest["spo2"] if latest["spo2"] is not None else 0

    return render_template('monitor.html', hr=hr, spo2=spo2)

if __name__ == '__main__':
    app.run(debug=True)