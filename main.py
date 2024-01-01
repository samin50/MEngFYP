"""
Main entry point for the application.
"""
import pygame
from src.pi4 import lcd_ui
from src.common.helper_functions import start_ui

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, enableInterface:bool=True) -> None:
        self.lcdUI = None
        if enableInterface:
            self.clk = pygame.time.Clock()
            self.lcdUI = lcd_ui.LCD_UI(self.clk)

if __name__ == "__main__":
    ENABLE_INTERFACE = True
    if ENABLE_INTERFACE:
        pygame.init()
        systemObj = Component_Sorter(ENABLE_INTERFACE)
        start_ui(
            [systemObj.lcdUI.draw],
            eventFunction=[systemObj.lcdUI.handle_events],
            exitFunction=[systemObj.lcdUI.cameraFeed.destroy],
            clock=systemObj.clk,
            manager=systemObj.lcdUI.manager,
            screen=systemObj.lcdUI.display
            )
