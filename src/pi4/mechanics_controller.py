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
from src.common.constants import GPIO_PINS, SPEED_MULTIPLIER, LIGHT_COLOUR, DEFAULT_SPEED, BIN_THRESHOLD, SWEEPER_MM_PER_STEP
from src.pi4.vision_handler import Vision_Handler
from src.pi4.lcd_ui import LCD_UI

class Sweeper_Controller:
    """
    Sweeper Controller - controls NEMA stepper motor and moves
    it to bin locations
    """
    def __init__(self) -> None:
        # Setup GPIO pins
        GPIO.setup(GPIO_PINS["SWEEPER_DIRECTION_PIN"], GPIO.OUT)
        GPIO.setup(GPIO_PINS["SWEEPER_STEP_PIN"], GPIO.OUT)
        GPIO.setup(GPIO_PINS["LIMIT_SWITCH_PIN"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # self.motor = GPIO.PWM(GPIO_PINS['SWEEPER_STEP_PIN'], 1)
        # self.motor.start(0)
        # Sorting variables
        self.speed = 0
        self.running = True
        self.isHomed = False
        self.sort = multiprocessing.Process(target=self.sort_process)
        self.steps = 0
        self.queue = Queue()
        self.map = dict()
        # Locks and events
        self.busyEvent = multiprocessing.Event()
        self.speedLock = multiprocessing.Lock()
        self.homingLock = multiprocessing.Lock()
        self.stepLock = multiprocessing.Lock()
        # Limit switch interrupt
        GPIO.add_event_detect(GPIO_PINS["LIMIT_SWITCH_PIN"], GPIO.FALLING, callback=self.limit_switch_interrupt)
        self.sort.start()

    def limit_switch_interrupt(self) -> None:
        """
        Limit switch interrupt
        """
        with self.homingLock:
            self.isHomed = True
        with self.stepLock:
            self.steps = 0
        # Also stop the motor
        self.stop()

    def stop(self) -> None:
        """
        Stop the sweeper
        """
        GPIO.output(GPIO_PINS['SWEEPER_DIRECTION_PIN'], GPIO.LOW)
        # self.motor.ChangeDutyCycle(0)
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
        while self.running:
            # Block until queue is received
            cls = self.queue.get(block=True)
            self.busyEvent.set()
            binNum = self.map[cls]
            # Move to bin
            self.go_bin(binNum)
            # Finished
            self.busyEvent.clear()

    def go_bin(self, binnum:int) -> None:
        """
        Make the motor move in time to reach the bin
        """
        self.write_speed(DEFAULT_SPEED)
        # Move until the sweeper is at the bin
        while abs(self.get_distance() - self.map[binnum]["pos"]) > BIN_THRESHOLD:
            distToTarget = self.get_distance() - self.map[binnum]["pos"]
            # Determine from distance how many steps to take
            steps = int(distToTarget / SWEEPER_MM_PER_STEP)
            # Set direction
            GPIO.output(GPIO_PINS['SWEEPER_DIRECTION_PIN'], GPIO.HIGH if distToTarget > 0 else GPIO.LOW)
            # Move with defined pulses
            for _ in range(steps):
                GPIO.output(GPIO_PINS['SWEEPER_STEP_PIN'], GPIO.HIGH)
                time.sleep(0.005 - self.get_speed() * 0.001)
                GPIO.output(GPIO_PINS['SWEEPER_STEP_PIN'], GPIO.LOW)
                time.sleep(0.001 - self.get_speed() * 0.001)
            # Add to steps
            self.add_steps(steps)
        # Reached the bin
        self.write_speed(0)

    def write_speed(self, speed:int) -> None:
        """
        Write the speed of the sweeper
        """
        with self.speedLock:
            self.speed = speed
        # self.motor.ChangeFrequency(SPEED_MULTIPLIER * abs(speed))
        # if speed == 0:
        #     self.motor.ChangeDutyCycle(0)
        # else:
        #     self.motor.ChangeDutyCycle(50)

    def get_speed(self) -> int:
        """
        Get the speed of the sweeper
        """
        with self.speedLock:
            return self.speed

    def add_steps(self, distance:int) -> None:
        """
        Write the distance of the sweeper
        """
        with self.stepLock:
            self.steps += distance

    def get_distance(self) -> int:
        """
        Get the distance of the sweeper
        """
        with self.stepLock:
            return self.steps * SWEEPER_MM_PER_STEP

class Conveyor_Controller:
    """
    Conveyor controller class
    Mulitproccessing-safe distance tracking for use by system controller
    """
    def __init__(self) -> None:
        # Set up the GPIO pins for the conveyor belt
        GPIO.setup(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.OUT)
        GPIO.setup(GPIO_PINS['CONVEYOR_STEP_PIN'], GPIO.OUT)
        self.motor = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 1)
        self.stop()
        self.speed = 0
        self.distance = 0
        self.startTime = time.time()
        # Locks
        self.distanceLock = multiprocessing.Lock()
        self.timeLock = multiprocessing.Lock()
        self.speedLock = multiprocessing.Lock()

    def start(self, speed:int=0) -> None:
        """
        Change the speed and direction of the conveyor belt
        """
        if speed == 0:
            self.stop()
        else:
            # If the conveyor is moving from 0, start the timer
            if self.speed == 0:
                self.write_time()
            else:
                self.write_distance()
                self.write_time()
            self.write_speed(speed)
            self.motor.ChangeDutyCycle(50)
            GPIO.output(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.HIGH if speed > 0 else GPIO.LOW)
            self.motor.ChangeFrequency(SPEED_MULTIPLIER * abs(speed))

    def stop(self) -> None:
        """
        Stop the conveyor belt
        """
        # Add to distance
        self.write_speed(0)
        self.write_distance()
        self.motor.ChangeDutyCycle(0)

    def write_time(self) -> None:
        """
        Write the time the conveyor belt has been running
        """
        with self.timeLock:
            self.startTime = time.time()

    def write_distance(self) -> None:
        """
        Write the distance travelled by the conveyor belt
        """
        with self.distanceLock:
            self.distance += (time.time() - self.get_start_time()) * self.get_speed()

    def write_speed(self, speed:int) -> None:
        """
        Write the speed of the conveyor belt
        """
        with self.speedLock:
            self.speed = speed

    def get_distance(self) -> float:
        """
        Get the distance travelled by the conveyor belt
        """
        with self.distanceLock:
            extraDistance = (time.time() - self.get_start_time()) * self.get_speed()
            return self.distance + extraDistance

    def get_start_time(self) -> float:
        """
        Get the time the conveyor belt started
        """
        with self.timeLock:
            return self.startTime

    def get_speed(self) -> int:
        """
        Get the speed of the conveyor belt
        """
        with self.speedLock:
            return self.speed
class WS2812B_Controller:
    """
    WS2812B controller class
    """
    def __init__(self, numleds: int = 17, speed: float = 5) -> None:
        self.numleds = numleds
        self.leds = None
        self.rainbowProcess = None
        self.colourProcess = None
        self.colour = [0, 0, 0]
        self.speed = speed
        self.queue = multiprocessing.Queue()
        self.initialize()
        self.status = 'ready'

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

    def change_colour_process(self, colour: tuple) -> None:
        """
        Change the colour of the strip
        """
        for i in range(self.leds.numPixels()):
            self.leds.setPixelColor(i, Color(colour[0], colour[1], colour[2]))
        self.leds.show()
        time.sleep(0.02)

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

    def set_status_light(self, status: str) -> None:
        """
        Set the status light - led 17
        """
        if status == 'ready':
            self.leds.setPixelColor(16, Color(0, 255, 0))
        elif status == 'busy':
            self.leds.setPixelColor(16, Color(255, 0, 0))
        elif status == 'working':
            self.leds.setPixelColor(16, Color(255, 255, 0))
        self.leds.show()
        self.status = status
class System_Controller:
    """
    Top level controller that abstracts the mechanics
    """
    def __init__(self, visionHandler:Vision_Handler) -> None:
        self.leds = WS2812B_Controller()
        self.conveyor = Conveyor_Controller()
        self.sweeper = Sweeper_Controller()
        self.lcdHandle = None
        self.visionHandler = visionHandler
        # IR Sensor
        GPIO.setup(GPIO_PINS["IR_SENSOR_PIN"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(GPIO_PINS["IR_SENSOR_PIN"], GPIO.FALLING, callback=self.interrupt)
        # Status light
        self.leds.set_status_light('ready')

    def set_lcd_handle(self, lcdHandle:LCD_UI) -> None:
        """
        Set the handle to the LCD UI
        """
        self.lcdHandle = lcdHandle

    def interrupt(self) -> None:
        """
        Interrupt function for when the beam is broken
        """
        beamProcess = multiprocessing.Process(target=self.beam_broken)
        beamProcess.start()

    def beam_broken(self) -> None:
        """
        Interupt function for when the beam is broken:
        Means there is a component to be sorted, the conveyor should stop
        Inference should be run
        """
        print("Beam broken")
        # If the system is busy but another component is detected, add to queue but send to refuse
        if self.sweeper.busyEvent.is_set():
            print("System busy, refusing component")
            self.sweeper.add_queue(('refuse', self.conveyor.get_distance()))
            return
        self.leds.set_status_light('busy')
        time.sleep(0.5)
        self.conveyor.stop()
        # Inference and get classification - status red
        cls = self.visionHandler.inference()
        # Add to queue, need to class and distance
        self.sweeper.add_queue(cls)
        # Start the conveyor
        self.conveyor.start(DEFAULT_SPEED)
        self.leds.set_status_light('working')
        # Wait until sweeper is done
        self.sweeper.busyEvent.wait()
        self.leds.set_status_light('ready')

if __name__ == "__main__":
    leds = WS2812B_Controller(speed=5)
