import adafruit_dht
import board
from RPLCD.i2c import CharLCD
from time import sleep
from kafka import KafkaProducer
import json
import os
from datetime import datetime

# Initialize the LCD
lcd = CharLCD('PCF8574', 0x27)

# Initialize the DHT sensor
dhtDevice = adafruit_dht.DHT22(board.D4)

# Kafka Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092',  # Update with your Kafka broker address
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# File to store data
data_file = os.path.join(os.path.dirname(__file__), 'sensor_data.txt')

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
    with open(data_file, 'a') as file:
        file.write(f"{data}\n")

try:
    while True:
        temperature, humidity = read_sensor()

        lcd.clear()
        if temperature is not None and humidity is not None:
            lcd.cursor_pos = (0, 0)
            lcd.write_string(f'Temp: {temperature:.1f}C')
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f'Humidity: {humidity:.1f}%')

            # Get the current time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Data with timestamp
            data = {'time': current_time, 'temperature': temperature, 'humidity': humidity}

            # Send data to Kafka
            producer.send('your_topic_name', data)

            # Write data to file
            write_to_file(data)

        else:
            lcd.write_string('Read error')

        sleep(5)

except KeyboardInterrupt:
    lcd.clear()
    print("Script stopped by user.")
