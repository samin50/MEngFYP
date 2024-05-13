import cv2
import RPi.GPIO as GPIO # type: ignore

# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)
# pylint: disable=all

# Initialize the camera
MOSFET_CONTROL_PIN = 18
GPIO.setup(MOSFET_CONTROL_PIN, GPIO.OUT)

# Set up PWM instance with frequency
pwm = GPIO.PWM(MOSFET_CONTROL_PIN, 2000)

# Start PWM with 50% duty cycle
pwm.start(20)
camera = cv2.VideoCapture(0)  # 0 is the default camera

try:
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()
        if not ret:
            break

        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # When everything is done, release the capture
    camera.release()
    cv2.destroyAllWindows()
    pwm.stop()
    GPIO.cleanup()
