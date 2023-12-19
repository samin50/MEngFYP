"""
Main entry point for the application.
"""
# pylint: disable=all
print("Hello World!")
import os
import pygame

# List of common SDL video drivers to test
drivers = ['directfb', 'fbcon', 'svgalib', 'x11', 'dga', 'ggi', 'vgl', 'aalib', 'dummy']

successful_drivers = []

for driver in drivers:
    try:
        # Set the SDL video driver to use
        os.environ['SDL_VIDEODRIVER'] = driver

        # Initialize Pygame
        pygame.init()
        info = pygame.display.Info()  # This line just to ensure it initializes fully
        print(f"Driver '{driver}' initialized successfully.")
        successful_drivers.append(driver)

        # Quit Pygame
        pygame.quit()
    except pygame.error:
        print(f"Driver '{driver}' failed to initialize.")

print("\nSuccessful drivers:", successful_drivers)