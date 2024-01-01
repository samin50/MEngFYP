"""
Custom Tkinter Frontend for the Pi4
Displays on the 7 inch Dfrobot LCD
"""
from customtkinter import CTk, CTkFont
from src.common.helper_functions import start_ui
from src.common.custom_ctk_widgets import CustomSlider

class LCD_UI:
    def __init__(self, root:CTk, fontObj:CTkFont, enableInterface:bool=True) -> None:
        self.root = root
        self.enableInterface = enableInterface
        self.font = fontObj
        if self.enableInterface:
            self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the UI
        """
        # UI Widgets
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        CustomSlider(self.root).grid(row=0, column=0)

if __name__ == "__main__":
    ENABLE_INTERFACE = True
    main, font = start_ui()
    systemObj = LCD_UI(main, font, ENABLE_INTERFACE)
    main.mainloop()
