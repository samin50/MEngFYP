"""
Mechanics controller
"""
import time
import random
import neopixel_spi
# import neopixel
import board
try:
    import RPi.GPIO as GPIO # type: ignore
except ImportError:
    import src.common.simulate as GPIO
from src.common.constants import GPIO_PINS, SPEED_MULTIPLIER


class Conveyor_Controller:
    """
    Conveyor controller class
    """
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # Set up the GPIO pins for the conveyor belt
        GPIO.setup(GPIO_PINS['CONVEYOR_ENABLE_PIN'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.OUT)
        self.motorSpeed = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 500)
        self.motorSpeed.start(50)
        self.stop()

    def change_speed(self, speed: int):
        """
        Change the speed and direction of the conveyor belt
        """
        if speed == 0:
            self.stop()
        else:
            self.motorSpeed.ChangeDutyCycle(50)
            GPIO.output(GPIO_PINS['CONVEYOR_ENABLE_PIN'], GPIO.HIGH)
            GPIO.output(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.HIGH if speed > 0 else GPIO.LOW)
            self.motorSpeed.ChangeFrequency(SPEED_MULTIPLIER * abs(speed))
            print(f"Frequency: {SPEED_MULTIPLIER * abs(speed)}")

    def stop(self):
        """
        Stop the conveyor belt
        """
        GPIO.output(GPIO_PINS['CONVEYOR_ENABLE_PIN'], GPIO.LOW)
        GPIO.output(GPIO_PINS['CONVEYOR_STEP_PIN'], GPIO.LOW)
        self.motorSpeed.ChangeDutyCycle(0)

if __name__ == "__main__":
    leds = neopixel_spi.NeoPixel_SPI(board.SPI(), 16)
    # leds = neopixel.NeoPixel(board.D18, 6, pixel_order=neopixel.GRB)
    # leds.fill((255, 0, 0))
    # leds.show()
    time.sleep(5)
    # leds.fill((0, 0, 0))
    leds.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    leds.show()
    # time.sleep(4)
    # leds.fill((0, 0, 0))
    # leds.show()
