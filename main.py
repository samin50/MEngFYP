"""
Main entry point for the application.
"""
import pygame
# Allow development on non-Raspberry Pi devices
try:
    import RPi.GPIO as GPIO
except ImportError:
    import src.common.simulate_gpio as GPIO
from src.pi4.lcd_ui import LCD_UI
from src.common.helper_functions import start_ui
from src.common.constants import GPIO_PINS, MOSFET_FREQ, LED_BRIGHTNESS

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, enableInterface:bool=True) -> None:
        self.lcdUI = None
        # LCD Setup
        if enableInterface:
            self.clk = pygame.time.Clock()
            self.lcdUI = LCD_UI(self.clk, self.change_led_brightness)
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
    if ENABLE_INTERFACE:
        pygame.init()
        systemObj = Component_Sorter(ENABLE_INTERFACE)
        start_ui(
            [systemObj.lcdUI.draw],
            eventFunction=[systemObj.lcdUI.handle_events],
            exitFunction=[systemObj.lcdUI.cameraFeed.destroy, systemObj.close],
            clock=systemObj.clk,
            manager=systemObj.lcdUI.manager,
            screen=systemObj.lcdUI.display
            )
