import adafruit_dht
import board
import RPi.GPIO as GPIO
from time import sleep, time
from kafka import KafkaProducer
import json
import os
from datetime import datetime

# Initialize the DHT sensor
dhtDevice = adafruit_dht.DHT22(board.D4)

# Kafka Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# File to store data
data_file = os.path.join(os.path.dirname(__file__), 'sensor_data.csv')

# Set up GPIO
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def read_sensor():
    for _ in range(3):
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            if humidity is not None and temperature is not None:
                return temperature, humidity
        except RuntimeError as error:
            sleep(2)
    return None, None

def write_to_file(data):
    file_exists = os.path.isfile(data_file)
    with open(data_file, 'a') as file:
        if not file_exists:
            file.write('Time,Temperature,Humidity\n')  # Write header
        file.write(f"{data['time']},{data['temperature']:.1f},{data['humidity']:.1f}\n")

try:
    while True:
        temperature, humidity = read_sensor()

        if temperature is not None and humidity is not None:
            # Turn on the LED
            GPIO.output(LED_PIN, GPIO.HIGH)

            # Print to console
            print(f'Temperature: {temperature:.1f}C, Humidity: {humidity:.1f}%')

            # Get the current time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Data with timestamp
            data = {'time': current_time, 'temperature': temperature, 'humidity': humidity}

            # Send data to Kafka
            producer.send('weather', data)

            # Write data to file
            write_to_file(data)

        else:
            # Turn off the LED in case of read error
            GPIO.output(LED_PIN, GPIO.LOW)
            print('Read error')

        sleep(5)

except KeyboardInterrupt:
    print("Script stopped by user.")
finally:
    # Turn off the LED and clean up GPIO
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
