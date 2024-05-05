"""
Mechanics controller
"""
import time
import threading
import colorsys
try:
    import RPi.GPIO as GPIO # type: ignore
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    from src.common.simulate import GPIO
    from src.common.simulate import PixelStrip, Color
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
    def __init__(self, numleds: int = 16, speed: float = 5) -> None:
        self.numleds = numleds
        self.leds = None
        self.rainbowThread = None
        self.colour = [0, 0, 0]
        self.speed = speed
        self.initialize()

    def initialize(self):
        """
        Initialize the LED strip
        """
        print("Initializing LED strip")
        self.leds = PixelStrip(self.numleds, 10, 800000, 10, False, 255, 0)
        self.leds.begin()
        self.rainbowThread = threading.Thread(target=self.rainbow_cycle)
        self.rainbowThread.start()

    def rainbow_cycle(self):
        """
        Draw rainbow that uniformly distributes itself across all pixels.
        """
        counter = 0
        step = 0
        while counter <= 192:
            for i in range(self.leds.numPixels()):
                newColour = colorsys.hsv_to_rgb((i * 256 / self.leds.numPixels() + step) % 256 / 256.0, 1.0, 1.0)
                self.leds.setPixelColor(i, Color(int(newColour[0]*255), int(newColour[1]*255), int(newColour[2]*255)))
            self.leds.show()
            time.sleep(0.02)
            step += self.speed
            counter += 1
        print("Rainbow cycle finished")

    def change_colour(self, colour: tuple) -> None:
        """
        Set the color of the strip, assumed as HSV
        """
        if colour[0] is not None:
            self.colour[0] = colour[0] / 180
        elif colour[1] is not None:
            self.colour[1] = colour[1] / 100
        elif colour[2] is not None:
            self.colour[2] = colour[2] / 100
        trueColour = colorsys.hsv_to_rgb(*tuple(self.colour))
        rgbColour = (int(trueColour[0]*255), int(trueColour[1]*255), int(trueColour[2]*255))
        print(f"Setting colour to {rgbColour}")
        for i in range(self.leds.numPixels()):
            self.leds.setPixelColor(i, Color(*rgbColour))

    def reset(self):
        """
        Reset the LED strip
        """
        print("Resetting LED strip")
        self.initialize()

if __name__ == "__main__":
    leds = WS2812B_Controller(speed=5)
