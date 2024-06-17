"""
All constants used in the project
"""
# UI Parameters
LCD_RESOLUTION = (1024, 600)
FPS_FONT_SIZE = 30
UI_FRAMERATE = 30
WIDGET_PADDING = 10
STAT_REFRESH_INTERVAL = 3000
BG_COLOUR = (128, 128, 128)
THEMEJSON = "./src/common/theme.json"
THEMEPARAMS = {
    "FONTSIZE" : 20,
    "labelTextColour" : "#FFFFFF"
}
SHOW_CURSOR = True
COLOURS = {
    "red" : "#FF0000",
    "yellow" : "#FFA500",
    "green" : "#00FF00",
}
# Vision Parameters
CAMERA_RESOLUTION = (640, 480)
CAMERA_DISPLAY_SIZE = (480, 360)
TRAINING_MODE_CAMERA_SIZE = (720, 540)
BOUNDING_BOX_COLOR = (148, 80, 166)
CAMERA_FRAMERATE = 5
CAPTURE_WINDOW = 10
# Custom Pygame Parameters
TOGGLE_TRUE_COLOUR = "#23C552"
TOGGLE_FALSE_COLOUR = "#F84F31"
TOGGLE_HOVER_COLOUR = "#AEAEAE"
# GPIO Parameters
GPIO_PINS = {
    "CONVEYOR_DIRECTION_PIN" : 27,
    # Need PWM pin for conveyor speed control
    "CONVEYOR_STEP_PIN" : 18,
    # LED pin
    "NEOPIXEL_PIN" : 10,
    # PWM pin for sweeper
    "SWEEPER_DIRECTION_PIN" : 6,
    "SWEEPER_STEP_PIN" : 13,
    # IR Beam break sensor
    "IR_SENSOR_PIN" : 7,
    # Limit switch
    "LIMIT_SWITCH_PIN" : 5
}
# Conveyor Parameters
DEFAULT_SPEED = 5
SPEED_MULTIPLIER = 80
LIGHT_COLOUR = (255, 218, 145)
BIN_THRESHOLD = 5
SWEEPER_MM_PER_STEP = 0.5
# Sweeper Parameters
MAX_POSITION = 100
MOVE_INCREMENT = 5
# Vision
CLASSIFIER_PATH = "./src/vision/models/final/classifier.pt"
