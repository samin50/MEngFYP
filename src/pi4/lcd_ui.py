"""
Pygame Frontend for the Pi4
Displays on the 7 inch Dfrobot LCD
"""
import os
import sys
import colorsys
import psutil
import pygame
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider, UILabel, UIButton
from src.common.constants import LCD_RESOLUTION, CAMERA_DISPLAY_SIZE, WIDGET_PADDING, STAT_REFRESH_INTERVAL, BG_COLOUR, THEMEJSON, SHOW_CURSOR, TRAINING_MODE_CAMERA_SIZE
from src.common.helper_functions import start_ui, wifi_restart
from src.common.custom_pygame_widgets import CustomToggleButton
from src.pi4.display_feed_pygame import CameraFeed

class LCD_UI:
    def __init__(self, clock:pygame.time.Clock, callbacks:dict={}, trainingMode:bool=False, resizeable:bool=False) -> None:
        # Setup UI
        self.display = pygame.display.set_mode(LCD_RESOLUTION, resizeable and (pygame.RESIZABLE | pygame.SCALED))
        pygame.display.set_caption("Component Sorter")
        self.clock = clock
        self.resolution = TRAINING_MODE_CAMERA_SIZE if trainingMode else CAMERA_DISPLAY_SIZE
        self.cameraSurface = pygame.Surface(self.resolution)
        self.cameraFeed = CameraFeed(self.resolution, self.cameraSurface, trainingMode)
        self.manager = pygame_gui.UIManager(LCD_RESOLUTION, theme_path=THEMEJSON, enable_live_theme_updates=False)
        self.UIElements = dict()
        # Setup Event
        self.statUpdateEvent = pygame.USEREVENT + 101
        pygame.time.set_timer(self.statUpdateEvent, STAT_REFRESH_INTERVAL)
        # Training mode setup
        self.init_ui_widgets(trainingMode)
        # Cursor
        if SHOW_CURSOR:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        # Callback functions
        self.stripResetCallback = callbacks.get("strip_reset_callback", lambda: None)
        self.colourCallback = callbacks.get("colour_callback", lambda _: None)
        self.conveyorSpeedCallback = callbacks.get("conveyor_speed_callback", lambda _: None)

    def init_ui_widgets(self, trainingMode) -> None:
        """
        Draw the UI widgets
        """
        # Widget Parameters
        labelLength = 220
        sliderHeight = 30
        offset = 15
        yOffset = offset
        offsetIncrement = 36
        buttonHeight = 50
        cornerOffset = (WIDGET_PADDING, 0)
        # Training mode
        if trainingMode:
            cornerOffset = (740, 0)
            global CAMERA_DISPLAY_SIZE # pylint:disable=global-statement
            CAMERA_DISPLAY_SIZE = (240, 360) # pylint:disable=redefined-outer-name, invalid-name
            labelLength = 50
        ## LEFT SIDE
        # Motor Speed
        yOffset += offsetIncrement
        self.UIElements["conveyor_speed_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0], CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="Conveyor Speed: 0",
            manager=self.manager
        )
        self.UIElements["conveyor_speed"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-labelLength, sliderHeight)),
            value_range=(-5, 5),
            start_value=0,
            manager=self.manager
        )
        # CPU Usage
        yOffset += offsetIncrement
        self.UIElements["cpu_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0], CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="CPU Usage: -%",
            manager=self.manager
        )
        # RAM Usage
        self.UIElements["ram_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="RAM Usage: -%",
            manager=self.manager
        )
        # Heatmap toggle button
        yOffset += offsetIncrement
        self.UIElements["heatmap_toggle"] = CustomToggleButton(
            relative_rect=pygame.Rect((cornerOffset[0], CAMERA_DISPLAY_SIZE[1]+yOffset), ((CAMERA_DISPLAY_SIZE[0]-WIDGET_PADDING)/2, buttonHeight)),
            text="Heatmap",
            manager=self.manager,
            object_id="#heatmap_toggle"
        )
        # ROI toggle button
        self.UIElements["roi_toggle"] = CustomToggleButton(
            relative_rect=pygame.Rect((cornerOffset[0]+(CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING)/2, CAMERA_DISPLAY_SIZE[1]+yOffset), ((CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING)/2, buttonHeight)),
            text="Enhance ROI",
            manager=self.manager,
            object_id="#roi_toggle"
        )
        # Exit Button
        yOffset += offsetIncrement*1.5
        self.UIElements["exit_button"] = UIButton(
            relative_rect=pygame.Rect((cornerOffset[0], CAMERA_DISPLAY_SIZE[1]+yOffset), ((CAMERA_DISPLAY_SIZE[0]-WIDGET_PADDING)/2, buttonHeight)),
            text="Exit",
            manager=self.manager
        )
        # Wifi Button
        self.UIElements["wifi_button"] = UIButton(
            relative_rect=pygame.Rect((cornerOffset[0]+(CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING)/2, CAMERA_DISPLAY_SIZE[1]+yOffset), ((CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING)/2, buttonHeight)),
            text="Wifi Restart",
            manager=self.manager
        )
        ## RIGHT SIDE
        if trainingMode:
            xOffset = cornerOffset[0]
            yOffset = WIDGET_PADDING
        else:
            xOffset = CAMERA_DISPLAY_SIZE[0] + 2*WIDGET_PADDING
            yOffset = WIDGET_PADDING
            CAMERA_DISPLAY_SIZE = (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 3*WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1])
        # Classification Label
        # self.UIElements["classification_label"] = UILabel(
        #     relative_rect=pygame.Rect((xOffset, yOffset), (labelLength, sliderHeight)),
        #     text="Classification:",
        #     manager=self.manager
        # )

        self.UIElements["hue_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset), (labelLength, sliderHeight)),
            text="Hue: 90",
            manager=self.manager
        )
        self.UIElements["hue_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset+labelLength+WIDGET_PADDING, yOffset), (CAMERA_DISPLAY_SIZE[0]-labelLength, sliderHeight)),
            value_range=(0, 180),
            start_value=90,
            click_increment=10,
            manager=self.manager
        )
        self.UIElements["saturation_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement), (labelLength, sliderHeight)),
            text="Saturation: 50",
            manager=self.manager
        )
        self.UIElements["saturation_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset+labelLength+WIDGET_PADDING, yOffset+offsetIncrement), (CAMERA_DISPLAY_SIZE[0]-labelLength, sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            click_increment=10,
            manager=self.manager
        )
        self.UIElements["value_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*2), (labelLength, sliderHeight)),
            text="Value: 50",
            manager=self.manager
        )
        self.UIElements["value_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset+labelLength+WIDGET_PADDING, yOffset+offsetIncrement*2), (CAMERA_DISPLAY_SIZE[0]-labelLength, sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            click_increment=10,
            manager=self.manager
        )
        self.UIElements["strip_reset_button"] = UIButton(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*3), (CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING, buttonHeight)),
            text="Reset Strip",
            manager=self.manager
        )
        self.UIElements["rgb_colour_code"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*4), (CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING, buttonHeight)),
            text="RGB: ",
            manager=self.manager
        )
        self.UIElements["hsv_colour_code"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*5), (CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING, buttonHeight)),
            text="HSV: ",
            manager=self.manager
        )
        self.UIElements["take_photo_button"] = UIButton(
            relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*6), (CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING, buttonHeight)),
            text="Take Photo",
            manager=self.manager
        )

    def handle_events(self, event:pygame.event) -> None:
        """
        Handle events from the UI
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.UIElements["conveyor_speed"]:
                self.UIElements["conveyor_speed_label"].set_text(f"Conveyor Speed: {(event.value)}")
                self.conveyorSpeedCallback(20 * event.value)
            # Colour sliders
            if event.ui_element == self.UIElements["hue_slider"]:
                colour = self.colourCallback((event.value, None, None))
                self.UIElements["hue_slider_label"].set_text(f"Hue: {event.value}")
                self.update_colour(colour)
            if event.ui_element == self.UIElements["saturation_slider"]:
                colour = self.colourCallback((None, event.value, None))
                self.UIElements["saturation_slider_label"].set_text(f"Saturation: {event.value}")
                self.update_colour(colour)
            if event.ui_element == self.UIElements["value_slider"]:
                colour = self.colourCallback((None, None, event.value))
                self.UIElements["value_slider_label"].set_text(f"Value: {event.value}")
                self.update_colour(colour)
        # Update the system stats
        if event.type == self.statUpdateEvent:
            cpuUsage = psutil.cpu_percent()
            ramUsage = psutil.virtual_memory().percent
            self.UIElements["cpu_usage_label"].set_text(f"CPU Usage: {cpuUsage}%")
            self.UIElements["ram_usage_label"].set_text(f"RAM Usage: {ramUsage}%")
        # Exit Button
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.UIElements["exit_button"]:
                self.cameraFeed.vision.destroy()
                pygame.quit()
                sys.exit()
            if event.ui_element == self.UIElements["heatmap_toggle"]:
                self.UIElements["heatmap_toggle"].toggle()
            if event.ui_element == self.UIElements["roi_toggle"]:
                self.UIElements["roi_toggle"].toggle()
            if event.ui_element == self.UIElements["wifi_button"]:
                wifi_restart()
            if event.ui_element == self.UIElements["strip_reset_button"]:
                self.stripResetCallback()
            if event.ui_element == self.UIElements["take_photo_button"]:
                image = self.cameraFeed.vision.get_frame()
                imageCounter = 0
                while os.path.exists(f"./src/vision/photos/image-{imageCounter:03}.jpg"):
                    imageCounter += 1
                pygame.image.save(image, f"./src/vision/photos/image-{imageCounter:03}.jpg")

    def draw(self) -> None:
        """
        Draw the UI
        """
        self.display.fill(BG_COLOUR)
        self.display.blit(self.cameraSurface, (WIDGET_PADDING, WIDGET_PADDING))

    def update_colour(self, colour) -> None:
        """
        Update the colour string on the display
        """
        hsv = colorsys.rgb_to_hsv(colour[0], colour[1], colour[2])
        rgbColour = [int(x*255) for x in colour]
        hsvColour = [int(x*255) for x in hsv]
        self.UIElements["rgb_colour_code"].set_text(f"RGB: {rgbColour}")
        self.UIElements["hsv_colour_code"].set_text(f"HSV: {hsvColour}")

if __name__ == "__main__":
    clk = pygame.time.Clock()
    pygame.init()
    systemObj = LCD_UI(clk)
    start_ui(
        [systemObj.draw],
        eventFunction=[systemObj.handle_events, systemObj.cameraFeed.event_handler],
        exitFunction=[systemObj.cameraFeed.vision.destroy],
        clock=clk,
        manager=systemObj.manager,
        screen=systemObj.display
        )
