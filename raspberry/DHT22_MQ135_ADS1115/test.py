import json
import os
from datetime import datetime
from time import sleep

import adafruit_ads1x15.ads1115 as ADS
import adafruit_dht
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn
from kafka import KafkaProducer

# Initialize the DHT sensor using the physical board pin number
DHT_PIN = board.D22
dhtDevice = adafruit_dht.DHT22(DHT_PIN)

# Initialize I2C bus and ADS1115 ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# MQ135 connected to channel 0 of ADS1115
mq135 = AnalogIn(ads, ADS.P0)

# Kafka Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# File to store data
data_file = os.path.join(os.path.dirname(__file__), 'sensors_data.csv')

def read_temperature_humidity():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return temperature, humidity
    except RuntimeError as error:
        print(f"Error reading DHT sensor: {error}")
        return None, None

def write_to_file(data):
    file_exists = os.path.isfile(data_file)
    with open(data_file, 'a') as file:
        if not file_exists:
            file.write('Time,Temperature,Humidity,CO2,NH3,NOx,Alcohol,Benzene,Smoke\n')
        file.write(f"{data['time']},{data['temperature']},{data['humidity']},{data['CO2']},{data['NH3']},{data['NOx']},{data['Alcohol']},{data['Benzene']},{data['Smoke']}\n")

def read_air_quality():
    return mq135.value

def interpret_air_quality(analog_value):
    co2_ppm = analog_to_co2(analog_value)
    nh3_ppm = analog_to_nh3(analog_value)
    nox_ppm = analog_to_nox(analog_value)
    alcohol_ppm = analog_to_alcohol(analog_value)
    benzene_ppm = analog_to_benzene(analog_value)
    smoke_ppm = analog_to_smoke(analog_value)
    return co2_ppm, nh3_ppm, nox_ppm, alcohol_ppm, benzene_ppm, smoke_ppm

# Placeholder functions for converting analog values to gas concentrations
def analog_to_co2(analog_value): 
    return analog_value * 0.1  # Example conversion formula

def analog_to_nh3(analog_value):
    return analog_value * 0.05  # Example conversion formula

def analog_to_nox(analog_value):
    return analog_value * 0.03  # Example conversion formula

def analog_to_alcohol(analog_value):
    return analog_value * 0.04  # Example conversion formula

def analog_to_benzene(analog_value):
    return analog_value * 0.02  # Example conversion formula

def analog_to_smoke(analog_value):
    return analog_value * 0.06  # Example conversion formula

try:
    while True:
        temperature, humidity = read_temperature_humidity()
        air_quality_raw = read_air_quality()
        co2_ppm, nh3_ppm, nox_ppm, alcohol_ppm, benzene_ppm, smoke_ppm = interpret_air_quality(air_quality_raw)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if temperature is not None and humidity is not None:
            data = {
                'time': current_time,
                'temperature': temperature,
                'humidity': humidity,
                'CO2': co2_ppm,
                'NH3': nh3_ppm,
                'NOx': nox_ppm,
                'Alcohol': alcohol_ppm,
                'Benzene': benzene_ppm,
                'Smoke': smoke_ppm
            }

            print(f"Time: {current_time}, Temperature: {temperature:.1f}C, Humidity: {humidity:.1f}%, CO2: {co2_ppm:.0f} ppm, NH3: {nh3_ppm:.0f} ppm, NOx: {nox_ppm:.0f} ppm, Alcohol: {alcohol_ppm:.0f} ppm, Benzene: {benzene_ppm:.0f} ppm, Smoke: {smoke_ppm:.0f} ppm")

            producer.send('environmental_data', data)

            write_to_file(data)

        sleep(2)

except KeyboardInterrupt:
    print("Script stopped by user.")
finally:
    dhtDevice.exit()