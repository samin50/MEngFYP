"""
Main entry point for the application.
"""
from src.pi4 import lcd_ui

class Component_Sorter:
    """
    Component Sorter class
    """
    def __init__(self, enableInterface:bool=True) -> None:
        self.lcdUI = lcd_ui.LCD_UI(enableInterface=enableInterface)

if __name__ == "__main__":
    ENABLE_INTERFACE = True
    systemObj = Component_Sorter(ENABLE_INTERFACE)
