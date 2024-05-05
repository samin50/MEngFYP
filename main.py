"""
Main entry point for the application.
"""
import pygame
# Allow development on non-Raspberry Pi devices
try:
    import RPi.GPIO as GPIO # type: ignore
    RESIZEFLAG = False
except ImportError:
    from src.common.simulate import GPIO
    RESIZEFLAG = True
from src.pi4.lcd_ui import LCD_UI
from src.pi4.mechanics_controller import Conveyor_Controller, WS2812B_Controller
from src.common.helper_functions import start_ui
from src.common.constants import GPIO_PINS

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, enableInterface:bool=True, trainingMode:bool=False) -> None:
        self.lcdUI = None
        GPIO.cleanup()
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_PINS["MOSFET_CONTROL_PIN"], GPIO.OUT)
        self.cameraLed = WS2812B_Controller()
        self.conveyorMotor = Conveyor_Controller()
        # LCD Setup
        if enableInterface:
            callbacks = {
                # "brightness_callback" : self.cameraLed.change_brightness,
                "colour_callback" : self.cameraLed.change_colour,
                "conveyor_speed_callback" : self.conveyorMotor.change_speed,
            }
            self.clk = pygame.time.Clock()
            self.lcdUI = LCD_UI(self.clk, callbacks, trainingMode, RESIZEFLAG)

    def close(self) -> None:
        """
        Close all the resources
        """
        self.conveyorMotor.stop()
        self.lcdUI.cameraFeed.destroy()
        GPIO.cleanup()

if __name__ == "__main__":
    ENABLE_INTERFACE = True
    TRAINING_MODE = False
    if ENABLE_INTERFACE:
        pygame.init()
        systemObj = Component_Sorter(ENABLE_INTERFACE, TRAINING_MODE)
        start_ui(
            loopFunction=[systemObj.lcdUI.draw],
            eventFunction=[systemObj.lcdUI.handle_events, systemObj.lcdUI.cameraFeed.event_handler],
            exitFunction=[systemObj.close],
            clock=systemObj.clk,
            manager=systemObj.lcdUI.manager,
            screen=systemObj.lcdUI.display,
            resolution=systemObj.lcdUI.resolution
            )
