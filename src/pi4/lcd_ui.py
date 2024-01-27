"""
Pygame Frontend for the Pi4
Displays on the 7 inch Dfrobot LCD
"""
import sys
import psutil
import pygame
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider, UILabel, UIButton
from src.common.constants import LCD_RESOLUTION, CAMERA_DISPLAY_SIZE, WIDGET_PADDING, STAT_REFRESH_INTERVAL, BG_COLOUR, THEMEJSON, LED_BRIGHTNESS, SHOW_CURSOR, TRAINING_MODE_CAMERA_SIZE
from src.common.helper_functions import start_ui
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
        self.brightnessCallback = callbacks.get("brightnessCallback", lambda _: None)

    def init_ui_widgets(self, trainingMode) -> None:
        """
        Draw the UI widgets
        """
        # Widget Parameters
        labelLength = 180
        sliderHeight = 30
        yOffset = 15
        offsetIncrement = 36
        buttonHeight = 50
        cornerOffset = (0, 0)
        # Training mode
        if trainingMode:
            cornerOffset = (760, 0)
            global CAMERA_DISPLAY_SIZE # pylint:disable=global-statement
            CAMERA_DISPLAY_SIZE = (240, 360) # pylint:disable=redefined-outer-name, invalid-name
            labelLength = 50
        # LED Ring Power
        self.UIElements["led_ring_power_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text=f"LED Power: {LED_BRIGHTNESS}%",
            manager=self.manager
        )
        self.UIElements["led_ring_power"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((cornerOffset[0]+2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=LED_BRIGHTNESS,
            manager=self.manager
        )
        # CPU Usage
        yOffset += offsetIncrement
        self.UIElements["cpu_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="CPU Usage: -%",
            manager=self.manager
        )
        self.UIElements["cpu_usage"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((cornerOffset[0]+2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=0,
            manager=self.manager
        )
        self.UIElements["cpu_usage"].disable()
        # RAM Usage
        yOffset += offsetIncrement
        self.UIElements["ram_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="RAM Usage: -%",
            manager=self.manager
        )
        self.UIElements["ram_usage"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((cornerOffset[0]+2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=0,
            manager=self.manager
        )
        self.UIElements["ram_usage"].disable()
        # Heatmap toggle button
        yOffset += offsetIncrement
        self.UIElements["heatmap_toggle"] = CustomToggleButton(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), ((CAMERA_DISPLAY_SIZE[0]-WIDGET_PADDING)/2, buttonHeight)),
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
        yOffset += offsetIncrement
        self.UIElements["exit_button"] = UIButton(
            relative_rect=pygame.Rect((cornerOffset[0]+WIDGET_PADDING, LCD_RESOLUTION[1]-WIDGET_PADDING-buttonHeight), (CAMERA_DISPLAY_SIZE[0], buttonHeight)),
            text="Exit",
            manager=self.manager
        )

    def handle_events(self, event:pygame.event) -> None:
        """
        Handle events from the UI
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.UIElements["led_ring_power"]:
                self.UIElements["led_ring_power_label"].set_text(f"LED Power: {event.value}%")
                self.brightnessCallback(event.value)
        # Update the system stats
        if event.type == self.statUpdateEvent:
            cpuUsage = psutil.cpu_percent()
            ramUsage = psutil.virtual_memory().percent
            self.UIElements["cpu_usage"].set_current_value(cpuUsage)
            self.UIElements["cpu_usage_label"].set_text(f"CPU Usage: {cpuUsage}%")
            self.UIElements["ram_usage"].set_current_value(ramUsage)
            self.UIElements["ram_usage_label"].set_text(f"RAM Usage: {ramUsage}%")
        # Exit Button
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.UIElements["exit_button"]:
                self.cameraFeed.destroy()
                pygame.quit()
                sys.exit()
            if event.ui_element == self.UIElements["heatmap_toggle"]:
                self.UIElements["heatmap_toggle"].toggle()
            if event.ui_element == self.UIElements["roi_toggle"]:
                self.UIElements["roi_toggle"].toggle()

    def draw(self) -> None:
        """
        Draw the UI
        """
        self.display.fill(BG_COLOUR)
        self.display.blit(self.cameraSurface, (WIDGET_PADDING, WIDGET_PADDING))

if __name__ == "__main__":
    pygame.init()
    clk = pygame.time.Clock()
    systemObj = LCD_UI(clk)
    start_ui(
        [systemObj.draw],
        eventFunction=[systemObj.handle_events, systemObj.cameraFeed.event_handler],
        exitFunction=[systemObj.cameraFeed.destroy],
        clock=clk,
        manager=systemObj.manager,
        screen=systemObj.display
        )
