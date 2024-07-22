import adafruit_dht
import board

dhtDevice = adafruit_dht.DHT22(board.D22)

try:
    temperature = dhtDevice.temperature
    humidity = dhtDevice.humidity
    print(f"Temperature: {temperature} C, Humidity: {humidity}%")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    dhtDevice.exit()