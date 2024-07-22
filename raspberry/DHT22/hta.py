import json
import os
from datetime import datetime
from time import sleep

import adafruit_dht
import board
import RPi.GPIO as GPIO
from kafka import KafkaProducer

# GPIO Mode (BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 17  # LED Pin
MQ135_PIN = 5      # MQ135 Air Quality Sensor Pin
DHT_PIN = board.D4  # DHT22 Data Pin

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(MQ135_PIN, GPIO.IN)

# Initialize the DHT sensor
dhtDevice = adafruit_dht.DHT22(DHT_PIN)

# Kafka Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# File to store data
data_file = os.path.join(os.path.dirname(__file__), 'sensors_data.csv')

def read_temperature_humidity():
    for attempt in range(2):
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            if humidity is not None and temperature is not None:
                return temperature, humidity
        except RuntimeError as error:
            sleep(1)  # Briefly pause before retrying
        except Exception as error:
            dhtDevice.exit()
            raise error
    return None, None

def write_to_file(data):
    file_exists = os.path.isfile(data_file)
    with open(data_file, 'a') as file:
        if not file_exists:
            file.write('Time,Temperature,Humidity,AirQuality\n')  # Write header
        file.write(f"{data['time']},{data['temperature']:.1f},{data['humidity']:.1f},{data['air_quality']}\n")

def read_air_quality():
    return GPIO.input(MQ135_PIN)

try:
    while True:
        temperature, humidity = read_temperature_humidity()
        air_quality = read_air_quality()

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if temperature is not None and humidity is not None:
            data = {
                'time': current_time,
                'temperature': temperature,
                'humidity': humidity,
                'air_quality': 'High' if air_quality else 'Normal'
            }

            print(f"Temperature: {temperature:.1f}C, Humidity: {humidity:.1f}%, Air Quality: {data['air_quality']}")

            producer.send('environmental_data', data)

            write_to_file(data)

        else:
            print('Sensor read error')

        GPIO.output(GPIO_TRIGGER, GPIO.HIGH if air_quality else GPIO.LOW)

        sleep(2)

except KeyboardInterrupt:
    print("Script stopped by user.")
finally:
    GPIO.cleanup()
    dhtDevice.exit()