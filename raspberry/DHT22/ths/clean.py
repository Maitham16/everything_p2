import RPi.GPIO as GPIO

# Clean up GPIO settings
GPIO.setwarnings(False)
GPIO.cleanup()
print("GPIO cleanup done.")
