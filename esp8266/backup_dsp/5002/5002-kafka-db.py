from flask import Flask, request, render_template_string
from confluent_kafka import Producer
from datetime import datetime
from influxdb import InfluxDBClient
import os

app = Flask(__name__)
producer = Producer({'bootstrap.servers': 'localhost:9092'})
influx_client = InfluxDBClient(host='localhost', port=8086, database='iot_s2')

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

temperature = 'N/A'
humidity = 'N/A'
last_update = 'Never'

def append_to_influx(last_update, temperature, humidity):
    json_body = [
        {
            "measurement": "environment",
            "time": last_update,
            "fields": {
                "temperature": float(temperature),
                "humidity": float(humidity)
            }
        }
    ]
    influx_client.write_points(json_body)

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
    </style>
</head>
<body>
    <div class="container">
        <h1>Weather Station Data</h1>
        <div class="sensor-data">
            <p>Temperature: {{ temperature }} &deg;C</p>
            <p>Humidity: {{ humidity }} %</p>
            <p>Last update on: {{ last_update }}</p>
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

@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    global temperature, humidity, last_update
    data = request.json
    temperature = data.get('temperature', 'N/A')
    humidity = data.get('humidity', 'N/A')
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_to_influx(last_update, temperature, humidity)
    producer.produce('iot_s2', key='sensor-data', value=str(data), callback=acked)
    producer.poll(0)
    producer.flush()
    return {"success": True}

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, temperature=temperature, humidity=humidity, last_update=last_update)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
