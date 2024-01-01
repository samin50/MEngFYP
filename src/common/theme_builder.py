"""
Theme builder for the Pygame GUI elements
"""
import json
from src.common.constants import THEMEJSON, THEMEPARAMS

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
            }
        }
        with open(THEMEJSON, "w", encoding="UTF-8") as handler:
            json.dump(jsonData, handler, indent=4)
        print("Theme Updated.")

if __name__ == "__main__":
    theme = StyleBuilder()
