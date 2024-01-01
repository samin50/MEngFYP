"""
Contains helper functions for the project.
"""
import pygame
from src.common.constants import UI_FRAMERATE

def start_ui(loopFunction:list, eventFunction:list=None, exitFunction:list=None, manager:callable=None, screen:pygame.display=None, clock:pygame.time.Clock=None) -> None:
    """
    Provide an event loop for standalone UIs
    """
    active = True
    while active:
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
