# things to write about:

## conveyor belt
conveyor mounting points were unstable due to a single anchor point, added a second to ensure it was physically constrained and could not rotate

designed custom motor driver board and enabled full microstepping as it was the quietest option

used yellow pastel paper backing to primarily give contrast against primarily blue resistor as colours were complimentary. The yellow hue would also help to cancel out the naturally blue white that the WS2182b leds were emitting, enabling a more white light on the components.

## led strip
cut apart and soldered WS2128b strip, as it is controllable by SPI and PWM

- learnt that PWM requires root privileges and was not viable due to unsafe practices and not being conventional
- learnt that SPI is somewhat unreliable in higher level libraries like neopixel
- implemented threading to allow the code to run parallised
  - due to increibly tight timing, and python global interpreter lock, threading was not the correct approach as the display and other code runs concurrently, and mulitprocessing was a solution
  - the lights would work when they run on their own only

multiprocessing was found to be more consistent but the main thread had to be paused to allow execution of the lighting in the background, meaning true parallism was not acheived. However, this is not a major concern as lighting will be not be manipulated during operation, and instead, the CV system will be relied upon to account for colour correction, and only manual calibration of the strip is neccassry. Another solution was considered  to offload the processing onto a microcontroller and communiate with it, but this was too much work for what could have been gained. 

In the end, it was shown to be a power supply issue, an inconsistent powersupply was thought to result in unstable GPIO control and due to SPI's precise timing, the Pi could not reliably control WS2182b strip.

After manual calibration, the lighting was kept at a constant (255, 255, 163). Noticebly, the blue channel is the weakest which may help to balance out the miscalibrated, blueish hue that the WS2182b leds tend to display. 


## vision
following sparseml documentation, the approach was to take a prepruned, pretrained, quanitsed model and then fine tune on my own dataset.

the learned low-level features from the pretraining (on the coco dataset) do transfer over to my dataset, and will speed up convergence

