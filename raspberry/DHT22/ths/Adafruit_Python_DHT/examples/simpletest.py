import adafruit_dht
import board
from time import sleep

# Initialize the DHT sensor
dhtDevice = adafruit_dht.DHT22(board.D4)  # Replace 'D4' with your actual GPIO pin

while True:
    try:
        # Read temperature and humidity
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('Failed to get reading. Try again!')

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])

    sleep(5)  # Wait for 5 seconds before next read
