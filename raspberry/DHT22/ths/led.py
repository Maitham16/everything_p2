import RPi.GPIO as GPIO
from time import sleep

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Check if GPIO mode has already been set
if GPIO.getmode() is None:
    GPIO.setmode(GPIO.BOARD)

# GPIO Setup using physical pin numbering
GPIO.setmode(GPIO.BOARD)
led_pin = 11
GPIO.setup(led_pin, GPIO.OUT)

# Test LED
try:
    print("Turning on LED.")
    GPIO.output(led_pin, GPIO.HIGH)
    sleep(5)
    print("Turning off LED.")
    GPIO.output(led_pin, GPIO.LOW)

except KeyboardInterrupt:
    print("Script stopped by user.")
    GPIO.cleanup()
