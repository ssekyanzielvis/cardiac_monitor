from flask import Flask, request, jsonify, render_template
import sqlite3
from contextlib import closing

app = Flask(__name__)

# Initialize database
def init_db():
    try:
        with closing(sqlite3.connect('cardiac_data.db')) as conn:
            with conn:
                conn.execute('''CREATE TABLE IF NOT EXISTS readings 
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                              hr INTEGER, 
                              spo2 INTEGER)''')
    except sqlite3.Error as e:
        print(f"Database error: {e}")

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
        with closing(sqlite3.connect('cardiac_data.db')) as conn:
            with conn:
                conn.execute("INSERT INTO readings (hr, spo2) VALUES (?, ?)", (hr, spo2))
    except Exception as e:
        return jsonify({'error': 'Failed to store data', 'details': str(e)}), 500

    return jsonify({'message': 'Data stored successfully', 'hr': hr, 'spo2': spo2}), 200

# Route to get latest reading
@app.route('/api/latest_reading', methods=['GET'])
def get_latest_reading():
    try:
        with closing(sqlite3.connect('cardiac_data.db')) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT hr, spo2 FROM readings ORDER BY timestamp DESC LIMIT 1")
                result = cursor.fetchone()
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    if result:
        return jsonify({'hr': result[0], 'spo2': result[1]})
    return jsonify({'error': 'No data available'}), 404

# Route to render the monitor template
@app.route('/')
def monitor():
    try:
        with closing(sqlite3.connect('cardiac_data.db')) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT hr, spo2 FROM readings ORDER BY timestamp DESC LIMIT 1")
                result = cursor.fetchone()
    except sqlite3.Error as e:
        return render_template('error.html', error=str(e)), 500

    hr = result[0] if result else 0
    spo2 = result[1] if result else 0

    return render_template('monitor.html', hr=hr, spo2=spo2)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)