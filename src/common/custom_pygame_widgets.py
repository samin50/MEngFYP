"""
Theme builder for the Pygame GUI elements
"""
import json
import pygame
from pygame_gui.elements import UIButton
from src.common.constants import THEMEJSON, THEMEPARAMS, TOGGLE_FALSE_COLOUR, TOGGLE_TRUE_COLOUR, TOGGLE_HOVER_COLOUR

class CustomToggleButton(UIButton):
    """
    This class is used to create a custom toggle button. It will change colours when toggled.
    """
    def __init__(self, relative_rect, text, manager, startValue=False, **kwargs):
        super().__init__(relative_rect, text, manager, **kwargs)
        self.toggled = startValue
        self.colours["hovered_bg"] = pygame.Color(TOGGLE_HOVER_COLOUR)
        self.colours["active_bg"] = pygame.Color("#FFFFFF")
        self.colours["hovered_text"] = pygame.Color("#FFFFFF")
        self.colours["normal_border"] = pygame.Color("#333333")
        self.toggle(startValue)

    def toggle(self, forceValue:bool=None):
        """
        Toggle the button
        """
        # Toggle Value
        if forceValue is None:
            self.toggled = not self.toggled
        else:
            self.toggled = forceValue
        # Change Colours
        if self.toggled:
            self.colours["normal_bg"] = pygame.Color(TOGGLE_TRUE_COLOUR)
        else:
            self.colours["normal_bg"] = pygame.Color(TOGGLE_FALSE_COLOUR)
        self.rebuild()

class StyleBuilder:
    """
    This class is used to update the Theme.json file with the constants defined in this file.
    """
    def __init__(self):
        # Update the JSON structure with the defined constants
        jsonData = {
            "label" : {
               "colours" : {
                    "normal_text" : THEMEPARAMS["labelTextColour"],
                 },
                "font" : {
                    "size" : THEMEPARAMS["FONTSIZE"],
                },
            },
            "button" : {
                "colours" : {
                    "normal_text" : THEMEPARAMS["labelTextColour"],
                },
                "font" : {
                    "size" : THEMEPARAMS["FONTSIZE"],
                },
                "misc" : {
                    "shadow_width": 0,
                },
            },
        }
        with open(THEMEJSON, "w", encoding="UTF-8") as handler:
            json.dump(jsonData, handler, indent=4)
        print("Theme Updated.")

if __name__ == "__main__":
    theme = StyleBuilder()
