"""
This file is used to allow the program to run on a computer without the functionality found on the Pi4.
This file emulates:
    - The GPIO pins
    - The PWM functionality
    - The camera feed
"""
# pylint: disable=all
import pygame
from src.common.constants import CAMERA_RESOLUTION
# Constants
BCM = 0
OUT = 0
# Functions
def setmode(_) -> None: pass
def setup(_, __) -> None: pass
def cleanup() -> None: pass
# Classes
# PWM emulation
class PWM:
    def __init__(self, _, __) -> None: pass
    def stop(self) -> None: pass
    def start(self, _) -> None: pass
    def ChangeDutyCycle(self, _) -> None: pass
    def ChangeFrequency(self, _) -> None: pass
# Camera emulation
class FakeCamera:
    def __init__(self, _) -> None:
        self.size = CAMERA_RESOLUTION
        self.font = pygame.font.SysFont("Roboto", 50)
        self.text = self.font.render("NO CAMERA", True, (255,255,255))
        self.textRect = self.text.get_rect()
        self.textRect.center = (self.size[0]//2, self.size[1]//2)
    def start(self) -> None: pass
    def query_image(self) -> bool: return True
    def get_image(self, frame:pygame.Surface) -> pygame.Surface:
        frame.fill((255,0,0))
        frame.blit(self.text, self.textRect)
        return frame
    def stop(self) -> None: pass
    def __del__(self) -> None: pass
# Neopixel Emulation
class NeoPixel_SPI:
    def __init__(self, _, __) -> None: pass
    def fill(self, _) -> None: pass
    def show(self) -> None: pass
    def __del__(self) -> None: pass
class SPI:
    def __init__(self) -> None: pass
    def __del__(self) -> None: pass