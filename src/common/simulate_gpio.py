"""
This file is used to allow the program to run on a computer without a GPIO.
"""
# pylint: disable=all
# Constants
BCM = 0
OUT = 0
# Functions
def setmode(_): pass
def setup(_, __): pass
def cleanup(): pass
# Classes
class PWM:
    def __init__(self, _, __): pass
    def stop(self): pass
    def start(self, _): pass
    def ChangeDutyCycle(self, _): pass
