"""
Main entry point for the application.
"""
import traceback
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
from src.common.helper_functions import start_ui
from src.pi4.mechanics_controller import System_Controller
from src.pi4.vision_handler import Vision_Handler
class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, trainingMode:bool=False, enableInference:bool=True) -> None:
        self.lcdUI = None
        GPIO.cleanup()
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        self.visionHandler = Vision_Handler(enableInference)
        self.systemController = System_Controller(self.visionHandler)
        # LCD Setup
        callbacks = {
            "colour_callback" : self.systemController.leds.change_colour,
            "strip_reset_callback" : self.systemController.leds.reset,
            "conveyor_speed_callback" : self.systemController.conveyor.start,
        }
        self.clk = pygame.time.Clock()
        self.lcdUI = LCD_UI(self.clk, self.visionHandler, callbacks, trainingMode, RESIZEFLAG)
        self.systemController.set_lcd_handle(self.lcdUI)

    def close(self) -> None:
        """
        Close all the resources
        """
        self.conveyorMotor.stop()
        self.lcdUI.cameraFeed.vision.destroy()
        GPIO.cleanup()

def run(trainingMode:bool, enableInference:bool=True) -> None:
    """
    Run the main application
    """
    keepRunning = True
    pygame.init()
    while keepRunning:
        try:
            systemObj = Component_Sorter(trainingMode, enableInference)
            start_ui(
                loopConditionFunc=systemObj.lcdUI.is_running,
                loopFunction=[systemObj.lcdUI.draw],
                eventFunction=[systemObj.lcdUI.handle_events, systemObj.lcdUI.visionHandler.event_handler],
                exitFunction=[systemObj.close],
                clock=systemObj.clk,
                manager=systemObj.lcdUI.manager,
                screen=systemObj.lcdUI.display,
                resolution=systemObj.lcdUI.resolution
                )
            keepRunning = systemObj.lcdUI.is_running()
        except Exception as e:
            # Try call close function
            try:
                systemObj.close()
            except:
                pass
            traceback.print_exc()
            clk = pygame.time.Clock()
            failScreen = FailScreen_UI(clk, str(e))
            start_ui(
                    loopConditionFunc=failScreen.is_running,
                    loopFunction=[failScreen.draw],
                    eventFunction=[failScreen.handle_events],
                    exitFunction=[],
                    clock=clk,
                    manager=failScreen.manager,
                    screen=failScreen.display,
                )
            keepRunning = failScreen.keepRunning
    pygame.quit()

if __name__ == "__main__":
    TRAINING_MODE = False
    PROFILER = False
    SNAKEVIZ = True
    INFERENCE = True
    # Run and optionally profile the application
    if PROFILER:
        import cProfile
        import subprocess
        profiler = cProfile.Profile()
        profiler.enable()
        profiler.run('run(TRAINING_MODE)')
        profiler.dump_stats('./profiles/profile.prof')
        if SNAKEVIZ:
            subprocess.Popen("snakeviz ./profiles/profile.prof", shell=True)
    else:
        run(TRAINING_MODE, INFERENCE)
