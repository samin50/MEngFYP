"""
Contains helper functions for the project.
"""
import subprocess
import time
import pygame
from src.common.constants import UI_FRAMERATE

def start_ui(loopConditionFunc:callable, loopFunction:list, eventFunction:list=None, exitFunction:list=None, manager:callable=None, screen:pygame.display=None, clock:pygame.time.Clock=None, resolution:tuple=(0, 1)) -> None:
    """
    Provide an event loop for standalone UIs
    """
    active = True
    aspectRatio = resolution[0] / resolution[1]
    while loopConditionFunc() and active:
        events = pygame.event.get()
        delta = clock.tick(UI_FRAMERATE) / 1000.0
        # Deal with events
        for e in events:
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                # Call the exit functions
                if exitFunction:
                    for func in exitFunction:
                        func()
                active = False
            # Resize event
            if e.type == pygame.VIDEORESIZE:
                newWidth, newHeight = e.w, e.h
                if newWidth / newHeight > aspectRatio:
                    newWidth = int(newHeight * aspectRatio)
                else:
                    newHeight = int(newWidth / aspectRatio)
                screen = pygame.transform.scale(screen, (newWidth, newHeight))
            # Update the UI Manager
            if manager:
                manager.process_events(e)
            # Call event functions
            if eventFunction:
                for func in eventFunction:
                    func(e)
        # Call the loop functions
        for func in loopFunction:
            func()
        # Update the UI Manager
        if manager:
            manager.update(delta)
            manager.draw_ui(screen)
        pygame.display.flip()
    pygame.quit()

def wifi_restart() -> None:
    """
    Restart the WiFi connection
    """
    subprocess.run(['sudo', 'ifdown', 'wlan0'], check=True)
    time.sleep(5)
    # Bring the Wi-Fi interface back up
    subprocess.run(['sudo', 'ifup', 'wlan0'], check=True)
