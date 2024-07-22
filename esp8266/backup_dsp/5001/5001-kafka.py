from flask import Flask, request, render_template_string
from confluent_kafka import Producer
from datetime import datetime
import csv
import os

app = Flask(__name__)

# Kafka Producer setup
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

temperature = 'N/A'
humidity = 'N/A'
last_update = 'Never'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Station Data</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #e4f0f5;
            color: #333;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            min-height: 100vh;
        }
        .container, .footer {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 400px;
            margin-bottom: 20px;
        }
        h1 {
            color: #0275d8;
        }
        p {
            font-size: 1.1rem;
            color: #555;
        }
        .sensor-data {
            background-color: #f9f9f9;
            margin: 20px 0;
            padding: 10px;
            border-radius: 5px;
        }
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

csv_file_path = 'esp8266_DHT11_S1.csv'

def append_to_csv(data):
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Temperature', 'Humidity'])
        writer.writerow(data)

@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    global temperature, humidity, last_update
    data = request.json
    temperature = data.get('temperature', 'N/A')
    humidity = data.get('humidity', 'N/A')
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append data to CSV
    append_to_csv([last_update, temperature, humidity])

    producer.produce('iot_s1', key='sensor-data', value=str(data), callback=acked)
    producer.poll(0)
    producer.flush()

    return {"success": True}

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, temperature=temperature, humidity=humidity, last_update=last_update)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
