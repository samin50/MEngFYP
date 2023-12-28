import cv2
# pylint: disable=all

# Initialize the camera
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
