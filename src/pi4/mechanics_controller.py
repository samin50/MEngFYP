"""
Mechanics controller
"""
import time
import threading
import colorsys
try:
    import RPi.GPIO as GPIO # type: ignore
    from neopixel_spi import NeoPixel_SPI as neopixel_spi
    from board import SPI
except ImportError:
    from src.common.simulate import GPIO
    from src.common.simulate import NeoPixel_SPI as neopixel_spi
    from src.common.simulate import SPI
    print("Simulating missing hardware!")
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
    def __init__(self, numleds: int = 16) -> None:
        self.leds = neopixel_spi(SPI(), numleds)
        self.currentColour = (0, 0, 0)
        self.stopFlag = threading.Event()
        self.colourLock = threading.Lock()
        self.newColourEvent = threading.Event()
        self.latestColour = (0, 0, 0)
        self.thread = threading.Thread(target=self.process_colour, daemon=True)
        self.thread.start()

    def process_colour(self) -> None:
        """
        Process the color change queue
        """
        while not self.stopFlag.is_set():
            # Wait for new colour
            self.newColourEvent.wait()
            self.newColourEvent.clear()
            time.sleep(5)
            with self.colourLock:
                colour = self.latestColour
            print(colour)
            self.leds.fill(colour)
            self.leds.show()
            self.currentColour = colour

    def change_colour(self, colour: tuple) -> None:
        """
        Change the color of the LED ring to the most recent color request
        """
        with self.colourLock:
            self.latestColour = colour
        self.newColourEvent.set()

    def change_brightness(self, brightness: int) -> None:
        """
        Change the brightness of the LED ring
        """
        colour = colorsys.hsv_to_rgb(float(brightness)/100, 0.5, 0.5)
        newColour = tuple(int(x * 255) for x in colour)
        self.change_colour(newColour)

    def stop(self):
        """
        Stop the current thread if it's running
        """
        self.change_colour((0, 0, 0))
        self.stopFlag.set()
        self.thread.join()

# Example usage
if __name__ == "__main__":
    controller = WS2812B_Controller()
    controller.change_color((255, 0, 0))
    time.sleep(6)  # Allow the previous change to complete before changing again
    controller.change_brightness(50)
    controller.stop()
