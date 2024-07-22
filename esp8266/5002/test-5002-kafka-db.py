from flask import Flask, request, render_template_string
from confluent_kafka import Producer
from datetime import datetime
from influxdb import InfluxDBClient

app = Flask(__name__)
producer = Producer({'bootstrap.servers': 'localhost:9092'})
influx_client = InfluxDBClient(host='localhost', port=8086, database='iot_s2')

SECRET_KEY = "35e48e8183b25d15b887f93ae8b31bb0"
last_update_time = None
device_id = 'Unknown'
temperature = 'N/A'
humidity = 'N/A'
startup_count = 'N/A'
status_indicator = "offline"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Station Data</title>
    <style>
        body {margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e4f0f5; color: #333; text-align: center; display: flex; justify-content: center; align-items: center; flex-direction: column; min-height: 100vh;}
        .container, .footer {background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 90%; max-width: 400px; margin-bottom: 20px;}
        h1 {color: #0275d8;}
        p {font-size: 1.1rem; color: #555;}
        .sensor-data {background-color: #f9f9f9; margin: 20px 0; padding: 10px; border-radius: 5px;}
        .status-indicator {width: 12px; height: 12px; border-radius: 50%; display: inline-block;}
        .online {background-color: #28a745;}
        .offline {background-color: #dc3545;}
    </style>
    <script>
        setInterval(function() { location.reload(); }, 30000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Weather Station Data</h1>
        <div class="sensor-data">
            <p>Device ID: {{ device_id }}</p>
            <p>Temperature: {{ temperature }} &deg;C</p>
            <p>Humidity: {{ humidity }} %</p>
            <p>Device Starts: {{ startup_count }}</p>
            <p>Last update on: {{ last_update }}</p>
            <p>Status: <span class="status-indicator {{ status_indicator }}"></span></p>
        </div>
    </div>
    <div class="footer">
        <p>Designed by Maitham Al-rubaye</p>
        <p>Supervised by Professor Atakan Aral</p>
        <p>University of Vienna</p>
        <p>2024</p>
    </div>
</body>
</html>
"""

def update_status():
    global status_indicator
    if last_update_time and (datetime.now() - last_update_time).seconds > 35:
        status_indicator = "offline"
    else:
        status_indicator = "online"

def append_to_influx(last_update, device_id, temperature, humidity):
    json_body = [
        {
            "measurement": "environment",
            "time": last_update,
            "tags": {
                "device_id": device_id
            },
            "fields": {
                "temperature": float(temperature),
                "humidity": float(humidity)
            }
        }
    ]
    influx_client.write_points(json_body)

def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {msg}: {err}")
    else:
        print(f"Message produced: {msg}")

@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    global temperature, humidity, last_update_time, device_id, startup_count
    data = request.json

    if data.get('secretKey') != SECRET_KEY:
        return {"error": "Unauthorized"}, 401

    temperature = data.get('temperature', 'N/A')
    humidity = data.get('humidity', 'N/A')
    device_id = data.get('deviceID', 'Unknown')
    startup_count = data.get('startCount', 'N/A')
    last_update_time = datetime.now()
    last_update = last_update_time.strftime("%Y-%m-%d %H:%M:%S")

    append_to_influx(last_update, device_id, temperature, humidity)

    producer.produce('iot_s2', key=device_id, value=str(data), callback=acked)
    producer.poll(0)
    producer.flush()

    return {"success": True}

@app.route('/')
def home():
    update_status()
    return render_template_string(
        HTML_TEMPLATE,
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
        startup_count=startup_count,
        last_update=last_update_time.strftime("%Y-%m-%d %H:%M:%S") if last_update_time else "Never",
        status_indicator=status_indicator
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
