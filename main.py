"""
Main entry point for the application.
"""
import sys
import pygame
# Allow development on non-Raspberry Pi devices
try:
    import RPi.GPIO as GPIO # type: ignore
    RESIZEFLAG = False
except ImportError:
    from src.common.simulate import GPIO
    RESIZEFLAG = True
from src.pi4.lcd_ui import LCD_UI
from src.pi4.fail_screen import FailScreen_UI
from src.pi4.mechanics_controller import Conveyor_Controller, WS2812B_Controller
from src.common.helper_functions import start_ui

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, trainingMode:bool=False) -> None:
        self.lcdUI = None
        GPIO.cleanup()
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        self.cameraLed = WS2812B_Controller()
        self.conveyorMotor = Conveyor_Controller(trainingMode)
        # LCD Setup
        callbacks = {
            "colour_callback" : self.cameraLed.change_colour,
            "strip_reset_callback" : self.cameraLed.reset,
            "conveyor_speed_callback" : self.conveyorMotor.change_speed,
        }
        self.clk = pygame.time.Clock()
        self.lcdUI = LCD_UI(self.clk, callbacks, trainingMode, RESIZEFLAG)

    def close(self) -> None:
        """
        Close all the resources
        """
        self.conveyorMotor.stop()
        self.lcdUI.cameraFeed.vision.destroy()
        GPIO.cleanup()

if __name__ == "__main__":
    TRAINING_MODE = True
    KEEPRUN = True
    PROFILER = False
    while KEEPRUN:
        try:
            pygame.init()
            systemObj = Component_Sorter(TRAINING_MODE)
            start_ui(
                loopFunction=[systemObj.lcdUI.draw],
                eventFunction=[systemObj.lcdUI.handle_events, systemObj.lcdUI.cameraFeed.event_handler],
                exitFunction=[systemObj.close],
                clock=systemObj.clk,
                manager=systemObj.lcdUI.manager,
                screen=systemObj.lcdUI.display,
                resolution=systemObj.lcdUI.resolution
                )
        except Exception as e:
            # Try call close function
            try:
                systemObj.close()
            except:
                pass
            print(e)
            clk = pygame.time.Clock()
            failScreen = FailScreen_UI(clk, str(e))
            start_ui(
                    loopFunction=[failScreen.draw],
                    eventFunction=[failScreen.handle_events],
                    exitFunction=[],
                    clock=clk,
                    manager=failScreen.manager,
                    screen=failScreen.display,
                )
            KEEPRUN = failScreen.keepRunning
    pygame.quit()
    sys.exit()
    