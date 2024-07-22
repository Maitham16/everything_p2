import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

# Function to append data to a log file
def log_sensor_data(temperature, humidity):
    with open("sensor_data.log", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}, Temperature: {temperature}, Humidity: {humidity}\n")

@app.route('/sensor_data', methods=['POST'])
def receive_data():
    sensor_data = request.json
    print(f"Received data: {sensor_data}")
    
    # Extract temperature and humidity from the received JSON
    temperature = sensor_data.get("temperature")
    humidity = sensor_data.get("humidity")
    
    # Log the sensor data
    log_sensor_data(temperature, humidity)
    
    return jsonify({"status": "success", "message": "Data received"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
