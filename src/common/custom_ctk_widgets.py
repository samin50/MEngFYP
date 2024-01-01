"""
Customised CTK widgets to ensure consistent look and feel.
Running this file will update a Theme.json file in the same directory.
"""
import json
from tkinter import Label
from customtkinter import set_appearance_mode, set_default_color_theme, CTk, CTkToplevel, CTkSlider, CTkLabel
from src.common.constants import DEFAULTHOVERTIME, STYLE, GRIDPADDING, THEMEJSON

class CustomGrid:
    """
    All custom tkinter widgets will have 3 pixel padding by default.
    """
    def grid(self, **kwargs) -> CTk:
        """
        Add the padding to the grid method.
        """
        kwargs.setdefault("padx", GRIDPADDING)
        kwargs.setdefault("pady", GRIDPADDING)
        super().grid(**kwargs)
        return self

class Tooltip:
    """
    This is the custom hover tooltip that is used for all custom tkinter widgets.
    Hovering over a widget will display a tooltip with the hovertext.
    """
    def __init__(self, root:CTk, text:str, delay:int=DEFAULTHOVERTIME):
        self.root = root
        self.text = text
        self.delay = delay
        self.afterID = None
        root.bind("<Enter>", self.schedule_show_tip)
        # root.bind("<Enter>", self.show_tip)
        root.bind("<Leave>", self.hide_tip)
        self.window = CTkToplevel(self.root)
        self.window.withdraw()
        self.window.wm_overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.label = Label(
            self.window,
            text=self.text,
            background="white",
            relief="solid",
            borderwidth=1,
            justify="left",
        )
        # Ensure that tooltips disappear eventually
        self.afterID = None

    def schedule_show_tip(self, _=None):
        """
        Show the tooltip after a delay.
        """
        if self.afterID is not None:
            self.root.after_cancel(self.afterID)
        self.afterID = self.root.after(self.delay, self.show_tip)

    def show_tip(self, _ = None):
        """
        Show the tooltip.
        """
        print("Showing tip")
        xCoord, yCoord, _, _ = self.root.bbox("insert")
        xCoord += self.root.winfo_rootx() + 25
        yCoord += self.root.winfo_rooty() + 25
        self.window.wm_geometry(f"+{xCoord}+{yCoord}")
        self.window.wm_attributes('-topmost', True)
        print(xCoord, yCoord)
        self.label.pack(ipadx=3, ipady=3)
        self.window.deiconify()
        self.check_mouse()

    def hide_tip(self, _ = None):
        """
        Hide the tooltip after the mouse leaves the widget.
        """
        print("Hiding tip")
        self.label.pack_forget()
        self.window.withdraw()

    def check_mouse(self):
        """
        Check if the mouse is still over the widget.
        """
        if not self.mouse_over_widget(self.root):
            self.hide_tip()
        else:
            self.root.after(self.delay, self.check_mouse)

    def mouse_over_widget(self, widget):
        """
        Grab the mouse coordinates and check if they are over the widget.
        """
        xCoord, yCoord = widget.winfo_pointerxy()
        widgetCoords = (
            widget.winfo_rootx(),
            widget.winfo_rooty(),
            widget.winfo_rootx() + widget.winfo_width(),
            widget.winfo_rooty() + widget.winfo_height(),
        )
        return (
            widgetCoords[0] <= xCoord <= widgetCoords[2]
            and widgetCoords[1] <= yCoord <= widgetCoords[3]
        )

class ValidIndicator(CustomGrid, Label):
    """
    Custom tkinter widget that features a red and green indicator.
    """
    def __init__(
        self, root:CTk, hovertext:str=None, delay:int=DEFAULTHOVERTIME, valid:bool=True, **kwargs
    ):
        self.isValid = None
        super().__init__(root, **kwargs)
        if hovertext is not None:
            #if font is set in kwargs, use that font
            if "font" in kwargs:
                self.hover = Tooltip(self, hovertext, delay)
            else:
                self.hover = Tooltip(self, hovertext, delay)
        if valid:
            self.set_valid()
        else:
            self.set_invalid()

    def set_valid(self):
        """
        Set the indicator to green.
        """
        self.isValid = True
        self.configure(text="✓", bg="lightgreen")

    def set_invalid(self):
        """
        Set the indicator to red.
        """
        self.isValid = False
        self.configure(text="✕", bg="brown2")

class CustomSlider(CustomGrid, CTkSlider):
    """
    Custom tkinter slider widget.
    """
    def __init__(
        self, root:CTk, hovertext:str=None, delay:int=DEFAULTHOVERTIME, **kwargs
    ):
        super().__init__(root, **kwargs)
        if hovertext is not None:
            self.hover = Tooltip(self, hovertext, delay)

class CustomLabel(CustomGrid, CTkLabel):
    """
    Custom tkinter label widget.
    """
    def __init__(
        self, root:CTk, hovertext:str=None, delay:int=DEFAULTHOVERTIME, **kwargs
    ):
        super().__init__(root, **kwargs)
        if hovertext is not None:
            self.hover = Tooltip(self, hovertext, delay)

class StyleBuilder:
    """
    This class is used to update the Theme.json file with the constants defined in this file.
    """
    def __init__(self):
        # Constants for colours
        backgroundLight = "gray95"
        backgroundDark = "gray8"
        foregroundLight = "gray82"
        foregroundDark = "gray20"
        primaryLight = "#3a7ebf"
        primaryDark = "#1f538d"
        accentLight = "#FFFFFF"
        accentDark = "#000000"
        # Constants for corner radius and border width
        cornerRadius = 6
        borderWidth = 0
        # Update the JSON structure with the defined constants
        jsonData = {
            "CTk": {"fg_color": [backgroundLight, backgroundDark]},
            "CTkToplevel": {"fg_color": [backgroundLight, backgroundDark]},
            "CTkFrame": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": ["gray90", "gray13"],
                "top_fg_color": ["gray85", "gray16"],
                "border_color": ["gray65", "gray28"],
            },
            "CTkButton": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": [primaryLight, primaryDark],
                "hover_color": ["#325882", "#14375e"],
                "border_color": ["#3E454A", "#949A9F"],
                "text_color": ["#DCE4EE", "#DCE4EE"],
                "text_color_disabled": ["gray74", "gray60"],
            },
            "CTkLabel": {
                "corner_radius": 0,
                "fg_color": "transparent",
                "text_color": ["gray14", "gray84"],
            },
            "CTkEntry": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": [foregroundLight, foregroundDark],
                "border_color": ["#979DA2", "#565B5E"],
                "text_color": ["gray14", "gray84"],
                "placeholder_text_color": ["gray52", "gray62"],
            },
            "CTkCheckBox": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": [primaryLight, primaryDark],
                "border_color": ["#3E454A", "#949A9F"],
                "hover_color": ["#325882", "#14375e"],
                "checkmark_color": ["#DCE4EE", "gray90"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"],
            },
            "CTkSwitch": {
                "corner_radius": 1000,
                "border_width": 3,
                "button_length": 0,
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": [accentLight, accentDark],
                "button_color": ["gray36", "#D5D9DE"],
                "button_hover_color": ["gray20", "gray100"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"],
            },
            "CTkRadiobutton": {
                "corner_radius": 1000,
                "border_width_checked": 6,
                "border_width_unchecked": 3,
                "fg_color": [primaryLight, primaryDark],
                "border_color": ["#3E454A", "#949A9F"],
                "hover_color": ["#325882", "#14375e"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray60", "gray45"],
            },
            "CTkProgressBar": {
                "corner_radius": 1000,
                "border_width": 0,
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": [accentLight, accentDark],
                "border_color": ["gray", "gray"],
            },
            "CTkSlider": {
                "corner_radius": 1000,
                "button_corner_radius": 1000,
                "border_width": 6,
                "button_length": 0,
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": ["gray40", "#AAB0B5"],
                "button_color": [accentLight, accentDark],
                "button_hover_color": ["#325882", "#14375e"],
            },
            "CTkOptionMenu": {
                "corner_radius": cornerRadius,
                "fg_color": [primaryLight, primaryDark],
                "button_color": ["#325882", "#14375e"],
                "button_hover_color": ["#234567", "#1e2c40"],
                "text_color": ["#DCE4EE", "#DCE4EE"],
                "text_color_disabled": ["gray74", "gray60"],
            },
            "CTkComboBox": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": ["#F9F9FA", "#343638"],
                "border_color": ["#979DA2", "#565B5E"],
                "button_color": ["#979DA2", "#565B5E"],
                "button_hover_color": ["#6E7174", "#7A848D"],
                "text_color": ["gray14", "gray84"],
                "text_color_disabled": ["gray50", "gray45"],
            },
            "CTkScrollbar": {
                "corner_radius": 1000,
                "border_spacing": 4,
                "fg_color": "transparent",
                "button_color": ["gray55", "gray41"],
                "button_hover_color": ["gray40", "gray53"],
            },
            "CTkSegmentedButton": {
                "corner_radius": cornerRadius,
                "border_width": borderWidth,
                "fg_color": ["#979DA2", "gray29"],
                "selected_color": [primaryLight, primaryDark],
                "selected_hover_color": ["#325882", "#14375e"],
                "unselected_color": ["#979DA2", "gray29"],
                "unselected_hover_color": ["gray70", "gray41"],
                "text_color": ["#DCE4EE", "#DCE4EE"],
                "text_color_disabled": ["gray74", "gray60"],
            },
            "CTkTextbox": {
                "corner_radius": cornerRadius,
                "border_width": 0,
                "fg_color": [foregroundLight, foregroundDark],
                "border_color": ["#90969A", "#565B5E"],
                "text_color": ["gray14", "gray84"],
                "scrollbar_button_color": ["gray55", "gray41"],
                "scrollbar_button_hover_color": ["gray40", "gray53"],
            },
            "CTkScrollableFrame": {"label_fg_color": ["gray80", "gray21"]},
            "DropdownMenu": {
                "fg_color": ["gray90", "gray20"],
                "hover_color": ["gray75", "gray28"],
                "text_color": ["gray14", "gray84"],
            },
            "CTkFont": {
                "macOS": {"family": "SF Display", "size": 13, "weight": "normal"},
                "Windows": {"family": "Roboto", "size": 13, "weight": "normal"},
                "Linux": {"family": "Roboto", "size": 13, "weight": "normal"},
            },
        }
        with open(THEMEJSON, "w", encoding="UTF-8") as handler:
            json.dump(jsonData, handler, indent=4)
        print("Theme Updated.")


if __name__ == "__main__":
    theme = StyleBuilder()
else:
    set_appearance_mode(STYLE)
    set_default_color_theme(THEMEJSON)
