"""
Mechanics controller
"""
import time
import random
try:
    import RPi.GPIO as GPIO # type: ignore
    import neopixel_spi.NeoPixel_SPI as neopixel_spi
    import board.SPI as SPI
except ImportError:
    import src.common.simulate as GPIO
    import src.common.simulate.NeoPixel_SPI as neopixel_spi
    import src.common.simulate.SPI as SPI
from src.common.constants import GPIO_PINS, SPEED_MULTIPLIER


class Conveyor_Controller:
    """
    Conveyor controller class
    """
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        # Set up the GPIO pins for the conveyor belt
        GPIO.setup(GPIO_PINS['CONVEYOR_ENABLE_PIN'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.OUT)
        self.motorSpeed = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 500)
        self.motorSpeed.start(50)
        self.stop()

    def change_speed(self, speed: int) -> None:
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

    def stop(self) -> None:
        """
        Stop the conveyor belt
        """
        GPIO.output(GPIO_PINS['CONVEYOR_ENABLE_PIN'], GPIO.LOW)
        GPIO.output(GPIO_PINS['CONVEYOR_STEP_PIN'], GPIO.LOW)
        self.motorSpeed.ChangeDutyCycle(0)

class WS2812B_Controller:
    """
    WS2812B controller class
    """
    def __init__(self) -> None:
        self.leds = neopixel_spi(SPI(), 16)
        self.change_color((0, 0, 0))

    def change_color(self, color: tuple) -> None:
        """
        Change the color of the LED ring
        """
        self.leds.fill(color)
        self.leds.show()

    def change_brightness(self, brightness: int) -> None:
        """
        Change the brightness of the LED ring
        """
        brightnessLevel = int(255 * brightness / 100)
        self.change_color((brightnessLevel, brightnessLevel, brightnessLevel))

if __name__ == "__main__":
    leds = neopixel_spi(SPI(), 16)
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
