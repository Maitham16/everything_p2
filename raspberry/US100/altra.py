import RPi.GPIO as GPIO
import time

# GPIO Mode (BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins for ultrasonic sensor
GPIO_TRIGGER = 17
GPIO_ECHO = 27

# Set GPIO Pins for RGB LED
GPIO_RED = 22
GPIO_GREEN = 23
GPIO_BLUE = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_RED, GPIO.OUT)
GPIO.setup(GPIO_GREEN, GPIO.OUT)
GPIO.setup(GPIO_BLUE, GPIO.OUT)

# Initially turn off all colors (since it's common anode)
GPIO.output(GPIO_RED, GPIO.HIGH)
GPIO.output(GPIO_GREEN, GPIO.HIGH)
GPIO.output(GPIO_BLUE, GPIO.HIGH)

def distance():
    # Send a 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2

    return distance

def control_rgb_led(dist):
    if dist < 10:
        # Red color
        GPIO.output(GPIO_RED, GPIO.LOW)
        GPIO.output(GPIO_GREEN, GPIO.HIGH)
        GPIO.output(GPIO_BLUE, GPIO.HIGH)
    elif dist < 30:
        # Blue Color
        GPIO.output(GPIO_RED, GPIO.HIGH)
        GPIO.output(GPIO_GREEN, GPIO.LOW)
        GPIO.output(GPIO_BLUE, GPIO.HIGH)
    else:
        # Green color
        GPIO.output(GPIO_RED, GPIO.HIGH)
        GPIO.output(GPIO_GREEN, GPIO.HIGH)
        GPIO.output(GPIO_BLUE, GPIO.LOW)

try:
    while True:
        dist = distance()
        print(f"Measured Distance = {dist:.1f} cm")
        control_rgb_led(dist)
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
