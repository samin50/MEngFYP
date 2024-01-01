"""
Displays the camera feed onto a customtkinter window
"""
import threading
from tkinter import Label
from customtkinter import CTk
import cv2
from PIL import Image, ImageTk
from src.common.constants import FRAMERATE
class CameraFeed(Label):
    def __init__(self, root:CTk, framerate:int=FRAMERATE, **kwargs) -> None:
        super().__init__(root, **kwargs)
        # Configure the root window
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        self.grid(row=0, column=0)
        self.bind("<Destroy>", lambda _: self.destroy())
        # Start the capture loop thread
        self.camera = cv2.VideoCapture(0)
        self.change_framerate(framerate)
        self.imgTk = None
        self.captureThread = threading.Thread(target=self.capture_loop, daemon=True)
        self.captureThread.start()

    def change_framerate(self, framerate:int) -> None:
        """
        Change the framerate of the camera
        """
        self.camera.set(cv2.CAP_PROP_FPS, framerate)
        self.frameperiod = int(1000 / framerate)

    def capture_loop(self) -> None:
        """
        Capture frames from the camera
        """
        _, frame = self.camera.read()
        opencvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(opencvImage)
        self.imgTk = ImageTk.PhotoImage(image=img)
        self.configure(image=self.imgTk)
        self.after(self.frameperiod, self.capture_loop)

    def destroy(self) -> None:
        """
        Destroy the camera object
        """
        self.camera.release()
        self.captureThread.join()
        super().destroy()

if __name__ == "__main__":
    main = CTk()
    CameraFeed(main).pack()
    main.mainloop()
