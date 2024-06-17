# pylint: disable=all
import RPi.GPIO as GPIO
import time
import random

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
endstop_pin = 26

# Set up the GPIO pin as an input with a pull-up resistor
GPIO.setup(endstop_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the callback function for the interrupt
def endstop_callback(channel):
    if GPIO.input(channel) == GPIO.LOW:
        print(f"Endstop triggered! {random.randint(0, 100)}")

# Set up the interrupt on the GPIO pin
GPIO.add_event_detect(endstop_pin, GPIO.FALLING, callback=endstop_callback, bouncetime=50)
print("Endstop interrupt set up!")

try:
    # Keep the program running to listen for interrupts
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()
