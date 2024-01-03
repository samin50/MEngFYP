"""
This module grabs a screenshot from the Raspberry Pi and allows easy labelling of the image.
"""
from tkinter import Label
import numpy
import cv2
import pyautogui
import pygetwindow
from PIL import Image, ImageTk
from customtkinter import CTk, CTkButton, CTkLabel, CTkFrame, StringVar
from src.vision.vsrc.constants import LOWER_THRESHOLD, UPPER_THRESHOLD, BORDER_WIDTH, CAMERA_BORDER, BORDER_COLOUR, \
    BORDER_COLOUR_FAILED, IMG_SIZE, MAX_ROWS, REALVNC_WINDOW_NAME, PADDING, DATA, RESISTOR_BODY_COLOUR

class RPIDatasetBuilder:
    def __init__(self, root:CTk) -> None:
        self.root = root
        self.root.title("RPi Dataset Builder")
        self.root.attributes("-topmost", True)
        # Variables
        self.screenshot = None
        self.componentName = StringVar()
        self.resistorValue = StringVar()
        self.resistorTrueValue = StringVar()
        self.selectedResistors = []
        # Grid weights
        self.root.grid_columnconfigure(1, weight=1)
        # Image display
        self.imgBorder = CTkLabel(self.root, text="", bg_color=BORDER_COLOUR_FAILED)
        self.imgDisplay = Label(self.imgBorder, text="", width=40, height=12, bg="#242424")
        self.imgBorder.grid(row=0, column=0, padx=PADDING, pady=PADDING)
        self.imgDisplay.grid(row=0, column=0, padx=CAMERA_BORDER, pady=CAMERA_BORDER)
        # Component Selection
        self.componentSelection = CTkFrame(self.root)
        for i, (component, data) in enumerate(DATA.items()):
            CTkLabel(self.componentSelection, text=data["shortcut"]).grid(row=i%MAX_ROWS, column=2*(i//MAX_ROWS), padx=PADDING, pady=2, sticky="nsew")
            CTkButton(self.componentSelection, text=component, command=lambda component=component: self.component_handler(component) \
                      ).grid(row=i%MAX_ROWS, column=2*(i//MAX_ROWS)+1, padx=PADDING, pady=2, sticky="nsew")
        # Resistor selection
        self.resistorSelection = CTkFrame(self.root)
        self.resistorSelection.grid_rowconfigure(MAX_ROWS, weight=1)
        for i, (colour, data) in enumerate(DATA["resistors"]["values"].items()):
            CTkLabel(self.resistorSelection, text=data[0]).grid(row=i%MAX_ROWS, column=2*(i//MAX_ROWS), padx=PADDING, pady=2, sticky="nsew")
            CTkButton(self.resistorSelection, text=colour, command=lambda data=data, colour=colour: self.resistor_handler(colour, data) \
                      ).grid(row=i%MAX_ROWS, column=2*(i//MAX_ROWS)+1, padx=PADDING, pady=2, sticky="nsew")
        self.resistorBody = None
        CTkLabel(self.resistorSelection, textvariable=self.resistorValue).grid(row=MAX_ROWS, column=5, padx=PADDING, pady=PADDING*2, sticky="nsew")
        CTkLabel(self.resistorSelection, textvariable=self.resistorTrueValue).grid(row=MAX_ROWS, column=1, padx=PADDING, pady=PADDING*2, sticky="nsew")
        # Filename builder
        self.filenameBuilder = CTkLabel(self.root, textvariable=self.componentName)
        self.filenameBuilder.grid(row=1, column=0, padx=PADDING, pady=PADDING, columnspan=2, sticky="nsew")
        # Save button
        self.saveButton = CTkButton(self.root, text="Save Image", state="disabled")
        self.saveButton.grid(row=2, column=0, padx=PADDING, pady=PADDING, columnspan=2, sticky="nsew")
        # Key bindings
        self.root.bind_all("<space>", self.capture_image)
        self.root.bind_all("<Escape>", lambda event: self.component_selection_panel())
        self.component_selection_panel()

    def capture_image(self, _:object) -> None:
        """
        Capture an image from the Raspberry Pi.
        """
        # Focus on the RealVNC window
        try:
            realVNCWindow = pygetwindow.getWindowsWithTitle(REALVNC_WINDOW_NAME)[0]
            realVNCWindow.activate()
            pygetwindow.getWindowsWithTitle("RPi Dataset Builder")[0].activate()
        except:
            self.imgBorder.configure(bg_color=BORDER_COLOUR_FAILED)
            return
        # Capture the image
        screenshotPil = pyautogui.screenshot(region=(realVNCWindow.left, realVNCWindow.top, realVNCWindow.width, realVNCWindow.height))
        # Convert to OpenCV format
        screenshotCv = numpy.array(screenshotPil)
        # Find the contours defined by the pink square
        mask = cv2.inRange(cv2.cvtColor(screenshotCv, cv2.COLOR_BGR2HSV), LOWER_THRESHOLD, UPPER_THRESHOLD)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
        # Find the largest contour in the mask
            largestContour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largestContour)
            x, y, w, h = x+BORDER_WIDTH, y+BORDER_WIDTH, w-(BORDER_WIDTH*2), h-(BORDER_WIDTH*2)
            cameraRegion = screenshotCv[y:y+h, x:x+w]
            cameraRegion = Image.fromarray(cameraRegion)
            self.screenshot = ImageTk.PhotoImage(cameraRegion.resize(IMG_SIZE, Image.NEAREST))
            self.imgDisplay.configure(width=IMG_SIZE[0], height=IMG_SIZE[1])
            self.imgDisplay.configure(image=self.screenshot)
            self.imgDisplay.image = self.screenshot
            self.imgBorder.configure(bg_color=BORDER_COLOUR)
        else:
            self.imgBorder.configure(bg_color=BORDER_COLOUR_FAILED)

    def component_selection_panel(self) -> None:
        """
        Display the component selection buttons.
        """
        self.componentSelection.grid(row=0, column=1, padx=(0, PADDING), pady=PADDING, sticky="nsew")
        self.resistorSelection.grid_remove()
        for _, (component, data) in enumerate(DATA.items()):
            self.root.bind(data["shortcut"], lambda _, component=component: self.component_handler(component))
        return

    def component_handler(self, component:str) -> None:
        """
        Handle when a component button is pressed or the corresponding shortcut is pressed.
        """
        self.componentName.set(DATA[component]["label"])
        self.componentSelection.grid_remove()
        if component == "resistors":
            for _, (colour, data) in enumerate(DATA["resistors"]["values"].items()):
                self.root.bind(data[0], lambda _, data=data, colour=colour: self.resistor_handler(colour, data))
            self.resistorSelection.grid(row=0, column=1, padx=PADDING, pady=(PADDING, 0), sticky="nsew")
            self.root.bind("<BackSpace>", lambda _: (self.selectedResistors.pop(), self.update_resistor_value()))
            self.update_resistor_value()
        return

    def resistor_handler(self, colour:str, _:tuple) -> None:
        """
        Handle when a resistor button is pressed or the corresponding shortcut is pressed.
        """
        self.selectedResistors.append(colour)
        self.update_resistor_value()
        return

    def update_resistor_value(self) -> None:
        """
        Update the resistor value.
        Resistor data:
        (shortcut, value, colour, tolerance)
        """
        valueDisplay = ""
        value = 0
        tolerance = 0
        resistorData = DATA["resistors"]["values"]
        # If 3 band resistor
        if len(self.selectedResistors) < 4:
            for colour in self.selectedResistors:
                valueDisplay += DATA["resistors"]["values"][colour][1]
                value = int(valueDisplay)
        # If 4 band resistor
        if len(self.selectedResistors) == 4:
            valueDisplay += resistorData[self.selectedResistors[0]][1]
            valueDisplay += resistorData[self.selectedResistors[1]][1]
            value = int(valueDisplay) * 10**int(resistorData[self.selectedResistors[2]][1])
            valueDisplay += "E" + resistorData[self.selectedResistors[2]][1]
            tolerance = str(resistorData[self.selectedResistors[3]][3])
            valueDisplay += "_" + tolerance
        # If 5 band resistor or more
        elif len(self.selectedResistors) >= 5:
            valueDisplay += resistorData[self.selectedResistors[0]][1]
            valueDisplay += resistorData[self.selectedResistors[1]][1]
            valueDisplay += resistorData[self.selectedResistors[2]][1]
            value = int(valueDisplay) * 10**int(resistorData[self.selectedResistors[3]][1])
            valueDisplay += "E" + resistorData[self.selectedResistors[3]][1]
            tolerance = str(resistorData[self.selectedResistors[4]][3])
            valueDisplay += "_" + tolerance
        # Draw resistor
        self.resistorBody = CTkLabel(self.resistorSelection, text="", bg_color=RESISTOR_BODY_COLOUR)
        self.resistorBody.grid(row=MAX_ROWS, column=3, padx=PADDING, pady=PADDING*2, sticky="nsew")
        self.resistorBody.grid_columnconfigure(0, weight=0)
        for index, resistor in enumerate(self.selectedResistors):
            CTkLabel(self.resistorBody, text="", bg_color=resistorData[resistor][2], width=5).grid(row=0, column=index, padx=5, pady=1, sticky="nsew")
        # Draw resistor label
        componentStr = DATA["resistors"]["label"] + "_"
        for resistor in self.selectedResistors:
            componentStr += resistor + "_"
        self.componentName.set(componentStr + valueDisplay)
        self.resistorValue.set(valueDisplay + " ohms")
        # Draw true resistor value
        if value < 1000:
            self.resistorTrueValue.set(str(value) + " ohms @ " + str(tolerance) + "%")
        elif value >= 1000 and value < 1000000:
            self.resistorTrueValue.set(str(value/1000) + "K ohms @ " + str(tolerance) + "%")
        elif value >= 1000000:
            self.resistorTrueValue.set(str(value/1000000) + "M ohms @ " + str(tolerance) + "%")
        return

if __name__ == "__main__":
    main = CTk()
    obj = RPIDatasetBuilder(main)
    main.mainloop()
