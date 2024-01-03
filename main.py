"""
Main entry point for the application.
"""
import pygame
import RPi.GPIO as GPIO
from src.pi4.lcd_ui import LCD_UI
from src.common.helper_functions import start_ui
from src.common.constants import GPIO_PINS, MOSFET_FREQ, LED_BRIGHTNESS

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, enableInterface:bool=True, trainingMode:bool=False) -> None:
        self.lcdUI = None
        # LCD Setup
        if enableInterface:
            callbacks = {
                "brightnessCallback" : self.change_led_brightness
            }
            self.clk = pygame.time.Clock()
            self.lcdUI = LCD_UI(self.clk, callbacks, trainingMode)
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_PINS["MOSFET_CONTROL_PIN"], GPIO.OUT)
        self.cameraLed = GPIO.PWM(GPIO_PINS["MOSFET_CONTROL_PIN"], MOSFET_FREQ)
        self.cameraLed.start(LED_BRIGHTNESS)

    def change_led_brightness(self, brightness:int) -> None:
        """
        Change the LED brightness
        """
        self.cameraLed.ChangeDutyCycle(brightness)

    def close(self) -> None:
        """
        Close all the resources
        """
        self.cameraLed.stop()
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
            exitFunction=[systemObj.lcdUI.cameraFeed.destroy, systemObj.close],
            clock=systemObj.clk,
            manager=systemObj.lcdUI.manager,
            screen=systemObj.lcdUI.display
            )
