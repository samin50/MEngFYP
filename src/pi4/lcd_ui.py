"""
Pygame Frontend for the Pi4
Displays on the 7 inch Dfrobot LCD
"""
import psutil
import pygame
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider, UILabel
from src.common.constants import LCD_RESOLUTION, CAMERA_DISPLAY_SIZE, WIDGET_PADDING, STAT_REFRESH_INTERVAL, BG_COLOUR
from src.common.helper_functions import start_ui
from src.pi4.display_feed_pygame import CameraFeed

class LCD_UI:
    def __init__(self, clock=pygame.time.Clock) -> None:
        # Setup UI
        self.display = pygame.display.set_mode(LCD_RESOLUTION)
        self.cameraSurface = pygame.Surface(CAMERA_DISPLAY_SIZE)
        self.clock = clock
        self.cameraFeed = CameraFeed(CAMERA_DISPLAY_SIZE, clock, self.cameraSurface)
        self.manager = pygame_gui.UIManager(LCD_RESOLUTION)
        self.UIElements = dict()
        # Setup Event
        self.statUpdateEvent = pygame.USEREVENT + 100
        pygame.time.set_timer(self.statUpdateEvent, STAT_REFRESH_INTERVAL)
        self.init_ui_widgets()

    def init_ui_widgets(self) -> None:
        """
        Draw the UI widgets
        """
        # LED Ring Power
        labelLength = 160
        sliderHeight = 30
        yOffset = 15
        offsetIncrement = 35
        self.UIElements["led_ring_power_label"] = UILabel(
            relative_rect=pygame.Rect((WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="LED Ring Power: 50%",
            manager=self.manager
        )
        self.UIElements["led_ring_power"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            manager=self.manager
        )
        # CPU Usage
        yOffset += offsetIncrement
        self.UIElements["cpu_usage_label"] = UILabel(
            relative_rect=pygame.Rect((WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="CPU Usage: -%",
            manager=self.manager
        )
        self.UIElements["cpu_usage"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            manager=self.manager
        )
        self.UIElements["cpu_usage"].disable()
        # RAM Usage
        yOffset += offsetIncrement
        self.UIElements["ram_usage_label"] = UILabel(
            relative_rect=pygame.Rect((WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (labelLength, sliderHeight)),
            text="RAM Usage: -%",
            manager=self.manager
        )
        self.UIElements["ram_usage"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((2*WIDGET_PADDING+labelLength, CAMERA_DISPLAY_SIZE[1]+yOffset), (CAMERA_DISPLAY_SIZE[0]-(labelLength+WIDGET_PADDING), sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            manager=self.manager
        )
        self.UIElements["ram_usage"].disable()

    def handle_events(self, event:pygame.event) -> None:
        """
        Handle events from the UI
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.UIElements["led_ring_power"]:
                self.UIElements["led_ring_power_label"].set_text(f"LED Ring Power: {event.value}%")
        # Update the system stats
        if event.type == self.statUpdateEvent:
            cpuUsage = psutil.cpu_percent()
            ramUsage = psutil.virtual_memory().percent
            self.UIElements["cpu_usage"].set_current_value(cpuUsage)
            self.UIElements["cpu_usage_label"].set_text(f"CPU Usage: {cpuUsage}%")
            self.UIElements["ram_usage"].set_current_value(ramUsage)
            self.UIElements["ram_usage_label"].set_text(f"RAM Usage: {ramUsage}%")

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
        eventFunction=[systemObj.handle_events],
        exitFunction=[systemObj.cameraFeed.destroy],
        clock=clk,
        manager=systemObj.manager,
        screen=systemObj.display
        )
