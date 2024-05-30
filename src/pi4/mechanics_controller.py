"""
Mechanics controller
"""
from queue import Queue
import time
import multiprocessing
import colorsys
try:
    import RPi.GPIO as GPIO # type: ignore
    from rpi_ws281x import PixelStrip, Color
    GPIO.setmode(GPIO.BCM)
    print("Using real hardware!")
except ImportError:
    from src.common.simulate import GPIO
    from src.common.simulate import PixelStrip, Color
    print("Simulating missing hardware!")
from src.common.constants import GPIO_PINS, SPEED_MULTIPLIER, LIGHT_COLOUR

class Sweeper_Controller:
    """
    Sweeper Controller - controls NEMA stepper motor and moves
    it to bin locations
    """
    def __init__(self, numBins:int, binDistance:int) -> None:
        # Setup GPIO pins
        GPIO.setup(GPIO_PINS["SWEEPER_DIRECTION_PIN"], GPIO.OUT)
        GPIO.setup(GPIO_PINS["SWEEPER_STEP_PIN"], GPIO.OUT)
        self.motor = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 1)
        self.motor.start(0)
        # Constants
        self.numBins = numBins
        self.binDistance = binDistance
        self.maxDistance = numBins * binDistance
        # Sorting variables
        self.running = True
        self.sort = multiprocessing.Process(target=self.sort_process)
        self.distance = 0
        self.queue = Queue()
        self.map = dict()

    def stop(self) -> None:
        """
        Stop the sweeper
        """
        GPIO.output(GPIO_PINS['SWEEPER_DIRECTION_PIN'], GPIO.LOW)
        self.motor.ChangeDutyCycle(0)
        self.running = False
        self.sort.join()

    def set_map(self, newmap:dict) -> None:
        """
        Set the map of bin to classification
        """
        self.map = newmap

    def add_queue(self, destination:tuple) -> None:
        """
        Add destination to queue in form of (time added, classification)
        """
        self.queue.put(destination)

    def sort_process(self) -> None:
        """
        Process that manages the sweeper
        """
        lastTime = time.time()
        while self.running:
            # Block until queue is received
            cls = self.queue.get()
            currentTime = time.time()

    def determine_path(self, binnum:int) -> None:
        """
        Make the motor move in time to reach the bin
        """

class Conveyor_Controller:
    """
    Conveyor controller class
    """
    def __init__(self) -> None:
        # Set up the GPIO pins for the conveyor belt
        GPIO.setup(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['CONVEYOR_STEP_PIN'], GPIO.OUT)
        self.motor = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 1)
        self.motor.start(50)
        self.stop()

    def change_speed(self, speed: int) -> None:
        """
        Change the speed and direction of the conveyor belt
        """
        if speed == 0:
            self.stop()
        else:
            self.motor.ChangeDutyCycle(50)
            GPIO.output(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.HIGH if speed > 0 else GPIO.LOW)
            self.motor.ChangeFrequency(SPEED_MULTIPLIER * abs(speed))

    def stop(self) -> None:
        """
        Stop the conveyor belt
        """
        GPIO.output(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.LOW)
        self.motor.ChangeDutyCycle(0)

class WS2812B_Controller:
    """
    WS2812B controller class
    """
    def __init__(self, numleds: int = 16, speed: float = 5) -> None:
        self.numleds = numleds
        self.leds = None
        self.rainbowProcess = None
        self.colourProcess = None
        self.colour = [0, 0, 0]
        self.speed = speed
        self.queue = multiprocessing.Queue()
        self.initialize()

    def initialize(self) -> None:
        """
        Initialize the LED strip
        """
        print("Initializing LED strip")
        self.leds = PixelStrip(self.numleds, GPIO_PINS["NEOPIXEL_PIN"], 800000, 10, False, 255, 0)
        self.leds.begin()
        self.rainbowProcess = multiprocessing.Process(target=self.rainbow_cycle, args=(self.queue, self.leds,))
        self.rainbowProcess.start()

    def rainbow_cycle(self, queue:multiprocessing.Queue, ledstrip: PixelStrip) -> None:
        """
        Draw rainbow that uniformly distributes itself across all pixels.
        """
        counter = 0
        step = 0
        while counter <= 128:
            for i in range(ledstrip.numPixels()):
                newColour = colorsys.hsv_to_rgb((i * 256 / ledstrip.numPixels() + step) % 256 / 256.0, 1.0, 1.0)
                ledstrip.setPixelColor(i, Color(int(newColour[0]*255), int(newColour[1]*255), int(newColour[2]*255)))
            ledstrip.show()
            time.sleep(0.02)
            step += self.speed
            counter += 1
            if not queue.empty():
                command = queue.get()
                if command == 'stop':
                    break
        print("Rainbow cycle finished")
        # Set all pixels to LIGHT_COLOUR
        for i in range(ledstrip.numPixels()):
            ledstrip.setPixelColor(i, Color(*LIGHT_COLOUR))
        ledstrip.show()

    def change_colour_process(self, colour: tuple) -> None:
        """
        Change the colour of the strip
        """
        for i in range(self.leds.numPixels()):
            self.leds.setPixelColor(i, Color(colour[0], colour[1], colour[2]))
        self.leds.show()
        time.sleep(0.02)

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
        self.colourProcess = multiprocessing.Process(target=self.change_colour_process, args=(rgbColour,))
        self.colourProcess.start()
        return trueColour

    def reset(self) -> None:
        """
        Reset the LED strip
        """
        print("Resetting LED strip")
        self.initialize()

    def stop(self) -> None:
        """
        Stop the LED strip
        """
        self.queue.put('stop')
        self.rainbowProcess.join()

if __name__ == "__main__":
    leds = WS2812B_Controller(speed=5)
