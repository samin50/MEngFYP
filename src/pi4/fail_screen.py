"""
Fail Screen UI used to restart system in case of failure
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel
from src.common.constants import LCD_RESOLUTION, WIDGET_PADDING, THEMEJSON
from src.common.helper_functions import start_ui, wifi_restart

class FailScreen_UI:
    def __init__(self, clock:pygame.time.Clock, errorMessage:str="Test") -> None:
        # Setup UI
        self.display = pygame.display.set_mode(LCD_RESOLUTION, (pygame.RESIZABLE | pygame.SCALED))
        self.manager = pygame_gui.UIManager(LCD_RESOLUTION, theme_path=THEMEJSON, enable_live_theme_updates=False)
        pygame.display.set_caption("Failure Screen")
        self.clock = clock
        self.keepRunning = True
        # Cursor
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        # Buttons
        buttonWidth = 400
        buttonHeight = 100
        # Crash text
        self.crashText = UILabel(
            relative_rect=pygame.Rect((LCD_RESOLUTION[0] // 2 - buttonWidth // 2, LCD_RESOLUTION[1] // 2 - buttonHeight * 3 - WIDGET_PADDING), (buttonWidth, buttonHeight)),
            text="System has crashed!",
            manager=self.manager
        )
        # Error text
        self.errorText = UILabel(
            relative_rect=pygame.Rect((LCD_RESOLUTION[0] // 2 - buttonWidth, LCD_RESOLUTION[1] // 2 - buttonHeight * 2.8), (buttonWidth * 2, buttonHeight * 2)),
            text=f"{errorMessage}",
            manager=self.manager
        )
        # Restart Button centered
        self.restartButton = UIButton(
            relative_rect=pygame.Rect((LCD_RESOLUTION[0] // 2 - buttonWidth // 2, LCD_RESOLUTION[1] // 2 - buttonHeight - WIDGET_PADDING), (buttonWidth, buttonHeight)),
            text="Restart",
            manager=self.manager
        )
        # Exit Button
        self.exitButton = UIButton(
            relative_rect=pygame.Rect((LCD_RESOLUTION[0] // 2 - buttonWidth // 2, LCD_RESOLUTION[1] // 2 + WIDGET_PADDING), (buttonWidth, buttonHeight)),
            text="Exit",
            manager=self.manager
        )
        # Wifi Restart Button
        self.wifiRestartButton = UIButton(
            relative_rect=pygame.Rect((LCD_RESOLUTION[0] // 2 - buttonWidth // 2, LCD_RESOLUTION[1] // 2 + buttonHeight + 3 * WIDGET_PADDING), (buttonWidth, buttonHeight)),
            text="Restart Wifi",
            manager=self.manager
        )

    def handle_events(self, event:pygame.event) -> None:
        """
        Handle events from the UI
        """
        # Handle UI Events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.exitButton:
                self.keepRunning = False
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.ui_element == self.restartButton:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.ui_element == self.wifiRestartButton:
                wifi_restart()

    def draw(self) -> None:
        """
        Draw the UI
        """
        self.display.fill((255, 0, 0))

if __name__ == "__main__":
    pygame.init()
    clk = pygame.time.Clock()
    systemObj = FailScreen_UI(clk)
    start_ui(
        [systemObj.draw],
        eventFunction=[systemObj.handle_events],
        exitFunction=[],
        clock=clk,
        manager=systemObj.manager,
        screen=systemObj.display
        )
