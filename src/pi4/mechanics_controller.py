"""
Mechanics controller
"""
import time
import threading
import colorsys
try:
    import RPi.GPIO as GPIO # type: ignore
    from neopixel_spi import NeoPixel_SPI as neopixel_spi
    from neopixel import NeoPixel as neopixel
    from board import SPI
    from board import D18
except ImportError:
    from src.common.simulate import GPIO
    from src.common.simulate import NeoPixel_SPI as neopixel_spi
    from src.common.simulate import SPI
    print("Simulating missing hardware!")
from src.common.constants import GPIO_PINS, SPEED_MULTIPLIER, LED_BRIGHTNESS


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
        self.leds = neopixel_spi(SPI(), numleds, pixel_order='GRB', auto_write=False)
        self.currentColour = (0, 0, 0)
        self.colourLock = threading.Lock()
        self.latestColour = (LED_BRIGHTNESS, LED_BRIGHTNESS, LED_BRIGHTNESS)
        self.processThread = None
        self.stopFlag = threading.Event()
        self.change_colour(self.latestColour)

    def _apply_colour_with_delay(self, delay: int, colour: tuple) -> None:
        """
        Apply the specified color after a delay
        """
        time.sleep(delay)
        with self.colourLock:
            self.leds.fill(colour)
            self.leds.show()
            self.currentColour = colour

    def change_colour(self, colour: tuple, delay: int = 12) -> None:
        """
        Change the color of the LED ring to the most recent color request
        """
        with self.colourLock:
            self.latestColour = colour

        self._restart_thread(self._apply_colour_with_delay, delay, colour)

    def _restart_thread(self, target, *args):
        """
        Restart the process thread with a new target and arguments
        """
        self.stop()

        # Restart the thread
        self.processThread = threading.Thread(target=target, args=args, daemon=True)
        self.stopFlag.clear()
        self.processThread.start()

    def change_brightness(self, brightness: int) -> None:
        """
        Change the brightness of the LED ring
        """
        # colour = colorsys.hsv_to_rgb(float(brightness)/100, 0.5, 0.5)
        # newColour = tuple(int(x * 255) for x in colour)
        newColour = (0, 0, brightness)
        self.change_colour(newColour)

    def stop(self):
        """
        Stop the current thread if it's running
        """
        self.stopFlag.set()
        if self.processThread:
            self.processThread.join()
            self.processThread = None

if __name__ == "__main__":
    # leds = neopixel_spi(SPI(), 8, pixel_order='GRB', auto_write=False)
    leds = neopixel(D18, 16)
    # leds.fill((0, 0, 0))
    # for i in range(10):
    #     leds.fill(colorsys.hsv_to_rgb(i/10, 0.5, 0.5))
    #     leds.show()
    #     time.sleep(4)
    time.sleep(12)
    leds.fill((16, 0, 16))
    leds.show()
    # # leds.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    # leds.fill((0, 0, 0))
    # leds.show()
