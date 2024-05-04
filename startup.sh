#!/bin/bash

startx & 
xset s off
xset s noblank
xset -dpms
# Check if the X server is responsive
while ! xset q &>/dev/null; do
    sleep 1
done
# python3 /home/dietpi/MEngFYP/main.py & 
