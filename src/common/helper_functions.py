"""
Contains helper functions for the project.
"""
from customtkinter import CTk, CTkFont
from src.common.constants import LCD_RESOLUTION, FONT, DISPLAY_CURSOR
def start_ui(font:CTkFont=None) -> None:
    """
    Start the UI
    """
    main = CTk()
    # Hide the cursor
    if not DISPLAY_CURSOR:
        main.config(cursor="none")
    main.geometry(LCD_RESOLUTION)
    if font is None:
        font = CTkFont(FONT)
    return main, font
