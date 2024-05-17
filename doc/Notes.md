# things to write about:

## cv model
the dataset tool was used to label ~100 of each component type

by the 150th image, it was discovered that some models support OBB (orientated bounding box) which encodes oritnation information which is crucial to read component values. the 150 labels generated were redone and the tool was redesigned to allow for this bounding box.

this gives several issues. first, there are no pre-sparsified models available for yolov8-obb models meaning i must sparsify my model myself. to use non obb datasets (aabb datasets), i have to develop my own training loop which trains the model on just obb for general identification, and then fine tuned on obb. which is far more work, as originally, the entire training pipeline is handled by sparseml's training pipeline.

however, not doing this work would result in a weaker model as the next stage would have to predict orientation especially in the case of resistors and ocr models for capacitor values. it was decided to train the custom model.


## conveyor belt
conveyor mounting points were unstable due to a single anchor point, added a second to ensure it was physically constrained and could not rotate

designed custom motor driver board and enabled full microstepping as it was the quietest option

used yellow pastel paper backing to primarily give contrast against primarily blue resistor as colours were complimentary. The yellow hue would also help to cancel out the naturally blue white that the WS2182b leds were emitting, enabling a more white light on the components.

# bin sweeper
orignal design had horizontal sweeping mechanism with many bearings, triggered with a flexible rod that would push the tail to force it in 'open' or 'closed' position. allows for multiple units sequentially, allowing infinite bins as the motor would simply need to only move towards gate X, ensuring that gates before it remain open. the horizontal design had a large area that would slow the system down as no components can be on the belt during this time, so the blocker is now lifted vertically but the same horizontal sweeping action is used to trigger the gates.

motor is carried on belt/cantry design inspired by the x gantry of 3d printers, such as ender 3. the timing belt and microstepping precision of the nema 17 motor allows for very precise and quick movement. keeping carriage weight down was essential. polyurathene rod was used as the flexible rod due to availability.

a horizontal to vertical motion mechnism using a linkage was designed to allow this. originally, 0.2mm spacing was used to enable the horizontal rod some clearance to move freely in the carriage, but was too tight for my specific printer. increased to 0.4mm.

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

