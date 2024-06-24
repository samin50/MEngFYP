"""
Mechanics controller
"""
# pylint:disable=unnecessary-lambda, unnecessary-lambda-assignment, using-constant-test, multiple-statements
import time
import multiprocessing
import threading
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
from src.common.constants import GPIO_PINS, CONV_MULTIPLIER, LIGHT_COLOUR, DEFAULT_SPEED, BOUNCETIME, MAX_POSITION, PATHS
from src.pi4.vision_handler import Vision_Handler
from src.pi4.lcd_ui import LCD_UI

class Sweeper_Controller:
    """
    Sweeper Controller - controls NEMA stepper motor and moves
    it to bin locations
    """
    def __init__(self, callbacks:dict={}) -> None:
        # Setup GPIO pins
        GPIO.setup(GPIO_PINS["SWEEPER_DIRECTION_PIN"], GPIO.OUT)
        GPIO.setup(GPIO_PINS["SWEEPER_STEP_PIN"], GPIO.OUT)
        GPIO.setup(GPIO_PINS["LIMIT_SWITCH_PIN"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Interrupts
        self.callbacks = callbacks
        GPIO.add_event_detect(GPIO_PINS["LIMIT_SWITCH_PIN"], GPIO.RISING, callback=self.__limit_switch, bouncetime=BOUNCETIME)
        # Variables
        self.homed = False
        manager = multiprocessing.Manager()
        self.distance = manager.Value('i', 0) # Distance moved by the sweeper
        # Locks
        self.expectHitEvent = multiprocessing.Event()
        self.expectHomeEvent = multiprocessing.Event()
        self.movingEvent = multiprocessing.Event()
        self.stopEvent = multiprocessing.Event()
        self.distanceLock = multiprocessing.Lock()

    def set_callbacks(self, callbacks:dict) -> None:
        """
        Set callback dict
        """
        self.callbacks = callbacks

    def __limit_switch(self, channel) -> bool:
        """
        Limit switch function - called when the limit switch is hit
        """
        if GPIO.input(channel) == GPIO.HIGH:
            return
        if self.expectHitEvent.is_set():
            self.expectHitEvent.clear()
            return
        self.stopEvent.set()
        self.movingEvent.clear()
        if self.expectHomeEvent.is_set():
            self.expectHomeEvent.clear()
            self.callbacks.get('write_lcd', lambda x: print(x))("Home")
            self.homed = True
            return True
        else:
            self.callbacks.get('write_lcd', lambda x: print(x))("Emergency")
            self.homed = False
            return False

    def __move(self, pulses:int, speed:int=1) -> None:
        """
        Move the sweeper to a specific pulse
        """
        if self.movingEvent.is_set():
            print("Sweeper is already moving")
            return
        if self.homed:
            with self.distanceLock:
                total = self.distance.value + pulses
                if total > MAX_POSITION:
                    print(f"Sweeper is at max position: {total}")
                    return
                if total < 0:
                    print(f"Sweeper is at min position: {total}")
                    return
                if total == 0:
                    self.expectHitEvent.set()
                    return
        self.movingEvent.set()
        distance = 0
        # If its expected that the pulses will lead to the limit switch being hit, expect it
        GPIO.output(GPIO_PINS["SWEEPER_DIRECTION_PIN"], GPIO.LOW if pulses > 0 else GPIO.HIGH)
        for _ in range(abs(pulses)):
            # Check if limit switch is hit
            if self.stopEvent.is_set():
                self.stopEvent.clear()
                self.distance.value = 0
                self.movingEvent.clear()
                return
            GPIO.output(GPIO_PINS["SWEEPER_STEP_PIN"], GPIO.HIGH)
            for _ in range(speed):
                if True: pass # add some delay
            GPIO.output(GPIO_PINS["SWEEPER_STEP_PIN"], GPIO.LOW)
            for _ in range(speed):
                if True: pass # add some delay
            distance += 1
        # Add to distance
        with self.distanceLock:
            self.distance.value += distance * (1 if pulses > 0 else -1)
            print(f"Distance, distance moved: {self.distance.value}, {distance}")
        self.movingEvent.clear()

    def home(self) -> None:
        """
        Home the sweeper
        """
        self.expectHomeEvent.set()
        multiprocessing.Process(target=self.__home).start()

    def __home(self) -> None:
        """
        Home the sweeper
        """
        moveProcess = multiprocessing.Process(target=self.__move, args=(20,))
        moveProcess.start()
        moveProcess.join()
        moveProcess = multiprocessing.Process(target=self.__move, args=(-MAX_POSITION,10,))
        moveProcess.start()
        moveProcess.join()

    def move(self, pulses:int) -> None:
        """
        Move the sweeper to a specific pulse
        """
        moveProcess = multiprocessing.Process(target=self.__move, args=(pulses,), daemon=True)
        moveProcess.start()
        self.callbacks.get("write_position", lambda x: print(x))(self.distance.value+pulses)

    def absolute_move(self, location:int) -> None:
        """
        Move the sweeper to a specific location
        """
        self.move(location - self.distance.value)

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
        self.manager = multiprocessing.Manager()
        self.speed = self.manager.Value('i', 0)
        self.distance = self.manager.Value('i', 0)
        self.startTime = time.time()
        # Locks
        self.speedLock = multiprocessing.Lock()
        self.distanceLock = multiprocessing.Lock()
        self.timeLock = multiprocessing.Lock()

    def start(self, speed:int=0) -> None:
        """
        Change the speed and direction of the conveyor belt
        """
        if speed == 0:
            self.stop()
        else:
            # If the conveyor is moving from 0, start the timer
            if self.speed.value == 0:
                self.write_time()
                self.motor.start(50)
            else:
                self.write_distance()
                self.write_time()
            self.write_speed(speed)
            GPIO.output(GPIO_PINS['CONVEYOR_DIRECTION_PIN'], GPIO.HIGH if speed > 0 else GPIO.LOW)
            self.motor.ChangeFrequency(CONV_MULTIPLIER * abs(speed))

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
            self.distance.value += (time.time() - self.get_start_time()) * self.get_speed()

    def write_speed(self, speed:int) -> None:
        """
        Write the speed of the conveyor belt
        """
        with self.speedLock:
            self.speed.value = speed
            print(speed)

    def get_distance(self) -> float:
        """
        Get the distance travelled by the conveyor belt
        """
        with self.distanceLock:
            extraDistance = (time.time() - self.get_start_time()) * self.get_speed()
            return self.distance.value + extraDistance

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
            return self.speed.value

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
        self.rainbowProcess = multiprocessing.Process(target=self.rainbow_cycle, args=(self.queue, self.leds,), daemon=True)
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
        self.colourProcess = multiprocessing.Process(target=self.change_colour_process, args=(rgbColour,), daemon=True)
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
        self.conveyorSpeed = 0
        self.enabled = False
        self.visionHandler = visionHandler
        # IR Sensor
        # GPIO.setup(GPIO_PINS["IR_SENSOR_PIN"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(GPIO_PINS["IR_SENSOR_PIN"], GPIO.FALLING, callback=self.interrupt)
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
        beamProcess = multiprocessing.Process(target=self.beam_broken, daemon=True)
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

    def sort(self, component:str) -> None:
        """
        Sorting function, triggered when inference is done
        or when a component is detected
        """
        if not self.enabled:
            print("System is disabled")
            self.lcdHandle.set_status("System is disabled", "red")
            return
        if not self.sweeper.homed:
            print("Sweeper is not homed")
            self.lcdHandle.set_status("Sweeper is not homed", "red")
            return
        # Begin sorting
        self.lcdHandle.set_status(f"Sorting {component}", "yellow")
        path = PATHS.get(component, PATHS['refuse'])
        threading.Thread(target=self.__sort, args=(path,), daemon=True).start()

    def __sort(self, path:int) -> None:
        """
        Sorting function, triggered when inference is done
        or when a component is detected
        """
        self.sweeper.absolute_move(path)
        start = time.time()
        speed = DEFAULT_SPEED
        self.conveyor.start(-speed)
        convPath = path + 2000 + 8000 # offset + arm length
        travelTime = float(convPath)/((speed*CONV_MULTIPLIER))
        print(f"Travel time: {travelTime}, {path}")
        while (time.time() - start) < travelTime:
            time.sleep(0.2)
        self.conveyor.stop()
        print(f"Sorting done in {time.time()-start} seconds")
        self.lcdHandle.set_status("Sorting done", "green")

    def set_conveyor_speed(self, speed:int) -> None:
        """
        Set conveyor speed
        """
        self.conveyorSpeed = speed
        self.conveyor.start(speed)

    def set_enabled(self, val:bool) -> None:
        """
        Enable system
        """
        self.enabled = val

if __name__ == "__main__":
    # leds = System_Controller(None)
    conveyor = Conveyor_Controller()
    conveyor.start(5)
    # motor = GPIO.PWM(GPIO_PINS['CONVEYOR_STEP_PIN'], 5)
    # motor.start(50)
