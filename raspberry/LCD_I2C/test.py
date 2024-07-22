from RPLCD.i2c import CharLCD
import time

def scroll_message(lcd, message, display_length=16, delay=0.4, repeat=5):
    """
    Manually scrolls a message across the LCD screen.

    :param lcd: The LCD instance.
    :param message: The message to scroll.
    :param display_length: The number of characters the display can show at once.
    :param delay: Delay between shifts.
    :param repeat: Number of times to repeat the scroll.
    """
    padded_message = ' ' * display_length + message + ' ' * display_length

    for _ in range(repeat):
        for i in range(len(message) + display_length):
            lcd.clear()
            lcd.write_string(padded_message[i:i+display_length])
            time.sleep(delay)

# Initialize the LCD
lcd = CharLCD('PCF8574', 0x27)

# Custom character definition for heart
heart = (
    0b00000,
    0b01010,
    0b11111,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000
)

# Create custom heart character
lcd.create_char(0, heart)

# Clear the LCD
lcd.clear()

# Messages with the heart character
first_message = "I " + chr(0) + " You BABA Hasan"
second_message = "I " + chr(0) + " You MAMA Sanaa"

# Scroll the messages
scroll_message(lcd, first_message, delay=0.2, repeat=2)
lcd.crlf()
scroll_message(lcd, second_message, delay=0.2, repeat=2)

# Wait for a while before clearing the display
time.sleep(5)
lcd.clear()
