"""
Constants for the Vision Trainer
"""
import numpy
# Constants
TITLE = "Vision Trainer"
RESOLUTION = "640x360"
PADDING = 5
# RPi Dataset Builder
REALVNC_WINDOW_NAME = "DietPi (DietPi)"
LOWER_THRESHOLD = numpy.array([148, 250, 250], numpy.uint8)
UPPER_THRESHOLD = numpy.array([152, 255, 255], numpy.uint8)
BORDER_WIDTH = 6
RECT_WIDTH = 2
RECT_COLOUR = "#FFFF00"
CAMERA_BORDER = 5
BORDER_COLOUR = "#00FF00"
BORDER_COLOUR_FAILED = "#FF0000"
IMG_SIZE = (480, 360)
MAX_ROWS = 5
RESISTOR_BODY_COLOUR = "#00CCFF"
PRECISION = 2
# Dataset
DATASET_PATH = "./src/vision/dataset"
DATA = {
    "resistors": {
        "label": "resistor",
        "num_label" : 0,
        "shortcut" : "r",
        "values" : {
            # (shortcut, value, colour, tolerance)
            "black": ("0", "0", "#000000", "0"),
            "brown": ("1", "1", "#8B4513", "1"),
            "red": ("2", "2", "#FF0000", "2"),
            "orange": ("3", "3", "#FFA500", "3"),
            "yellow": ("4", "4", "#FFFF00", "4"),
            "green": ("5", "5", "#00FF00", "0.5"),
            "blue": ("6", "6", "#0000FF", "0.25"),
            "violet": ("7", "7", "#EE82EE", "0.1"),
            "grey": ("8", "8", "#808080", "0.05"),
            "white": ("9", "9", "#FFFFFF", "0"),
            "gold": ("-", "-1", "#FFD700", "5"),
            "silver": ("=", "-2", "#C0C0C0", "10"),
        },
    },
    "capacitors": {
        "label": "capacitor",
        "num_label" : 1,
        "shortcut" : "c",
    },
    "ceramic_cap": {
        "label": "ceramic_capacitor",
        "num_label" : 2,
        "shortcut" : "e",
    },
    "inductors": {
        "label": "inductor",
        "num_label" : 3,
        "shortcut" : "i",
    },
    "diodes": {
        "label": "diode",
        "num_label" : 4,
        "shortcut" : "d",
    },
    "mosfets": {
        "label": "mosfet",
        "num_label" : 5,
        "shortcut" : "m",
    },
    "transistors": {
        "label": "transistor",
        "num_label" : 6,
        "shortcut" : "t",
    },
    "leds": {
        "label": "led",
        "num_label" : 7,
        "shortcut" : "l",
    },
    "wires" : {
        "label": "wire",
        "num_label" : 8,
        "shortcut" : "w",
    },
    "ics": {
        "label": "ic",
        "num_label" : 9,
        "shortcut" : "s",
    },
}
