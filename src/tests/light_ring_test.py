# pylint: disable=all
import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    import src.common.simulate_gpio as GPIO

# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)

# Set up the GPIO channel
MOSFET_CONTROL_PIN = 18
SPEED = 0.01
GPIO.setup(MOSFET_CONTROL_PIN, GPIO.OUT)

# Set up PWM instance with frequency
pwm = GPIO.PWM(MOSFET_CONTROL_PIN, 160)

# Start PWM with 50% duty cycle
pwm.start(50)

try:
    # Loop to fade the LED ring in and out
    while True:
        for i in range(100, -1, -1):
            pwm.ChangeDutyCycle(i)
            print("Duty cycle:", i)
            time.sleep(SPEED)
        for i in range(100):
            pwm.ChangeDutyCycle(i)
            print("Duty cycle:", i)
            time.sleep(SPEED)
except KeyboardInterrupt:
    pass

# Stop and cleanup on exit
pwm.stop()
GPIO.cleanup()
