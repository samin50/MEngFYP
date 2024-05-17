"""
This module grabs a screenshot from the Raspberry Pi and allows easy labelling of the image.
"""
import os
from tkinter import Canvas, ALL
import numpy
import cv2
import pyautogui
import pygetwindow
from PIL import Image, ImageTk
from customtkinter import CTk, CTkButton, CTkLabel, CTkFrame, CTkEntry, StringVar, IntVar
from src.vision.vsrc.constants import LOWER_THRESHOLD, UPPER_THRESHOLD, BORDER_WIDTH, CAMERA_BORDER, BORDER_COLOUR, \
    BORDER_COLOUR_FAILED, DISPLAY_IMG_SIZE, MAX_ROWS, REALVNC_WINDOW_NAME, PADDING, DATA, RESISTOR_BODY_COLOUR, DATASET_PATH, RECT_WIDTH, RECT_COLOUR, PRECISION, IMG_SIZE

class RPIDatasetBuilder:
    def __init__(self, root:CTk, dataPath:str=False, labelPath:str=None) -> None:
        self.root = root
        # If datapath specified get a list of all the images in the folder
        self.dataSet = None
        self.dataPath = None
        self.labelPath = labelPath
        self.dataIndex = 0
        if dataPath:
            self.dataPath = dataPath
            self.dataSet = os.listdir(dataPath)
        self.root.title("RPi Dataset Builder")
        self.root.attributes("-topmost", True)
        # Variables
        self.screenshot = None
        self.componentName = StringVar()
        self.filename = StringVar()
        self.saveNum = IntVar()
        self.saveStr = StringVar(value="-")
        self.currentComponent = ""
        self.rectangleStartBounds = (0, 0)
        self.rectangleEndBounds = (0, 0)
        # Component variables
        self.resistorValue = StringVar()
        self.resistorTrueValue = StringVar()
        self.selectedResistors = []
        self.capacitorCapacity = StringVar()
        self.capacitorVoltage = StringVar()
        # Grid weights
        self.root.grid_columnconfigure(1, weight=1)
        # Image display
        self.imgBorder = CTkLabel(self.root, text="", bg_color=BORDER_COLOUR_FAILED)
        self.imgDisplay = Canvas(self.imgBorder, width=DISPLAY_IMG_SIZE[0], height=DISPLAY_IMG_SIZE[1], bg="#242424")
        self.imgBorder.grid(row=0, column=0, padx=PADDING, pady=PADDING)
        self.imgDisplay.grid(row=0, column=0, padx=CAMERA_BORDER, pady=CAMERA_BORDER)
        self.rectangle = self.imgDisplay.create_rectangle(0, 0, 0, 0, outline=RECT_COLOUR, width=RECT_WIDTH)
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
        # Capacitor selection
        self.capacitorSelection = CTkFrame(self.root)
        CTkLabel(self.capacitorSelection, text="Capacity:").grid(row=0, column=0, padx=PADDING, pady=PADDING, sticky="nsew")
        CTkLabel(self.capacitorSelection, text="Voltage:").grid(row=1, column=0, padx=PADDING, pady=PADDING, sticky="nsew")
        CTkEntry(self.capacitorSelection, textvariable=self.capacitorCapacity).grid(row=0, column=1, padx=PADDING, pady=PADDING, sticky="nsew")
        CTkEntry(self.capacitorSelection, textvariable=self.capacitorVoltage).grid(row=1, column=1, padx=PADDING, pady=PADDING, sticky="nsew")
        CTkEntry(self.capacitorSelection).grid(row=2, column=0, columnspan=2, padx=PADDING, pady=PADDING, sticky="nsew")
        # Filename builder
        self.filenameLabel = CTkLabel(self.root, textvariable=self.filename)
        self.filenameLabel.grid(row=1, column=0, padx=PADDING, pady=PADDING, sticky="nsew")
        self.filenameBuilder = CTkLabel(self.root, textvariable=self.componentName)
        self.filenameBuilder.grid(row=1, column=1, padx=PADDING, pady=PADDING, sticky="nsew")
        # Save button
        self.saveButton = CTkButton(self.root, text="Save Image (s)", state="disabled", command=self.save_image)
        self.saveButton.grid(row=2, column=1, padx=PADDING, pady=PADDING, sticky="nsew")
        self.saveLabel = CTkLabel(self.root, textvariable=self.saveStr, text_color="green")
        self.saveLabel.grid(row=2, column=0, padx=PADDING, pady=PADDING, sticky="nsew")
        # Key bindings
        self.root.bind_all("<Escape>", lambda _: self.component_selection_panel())
        self.root.bind_all("<Return>", lambda _: self.save_image())
        if dataPath:
            self.root.bind_all("<Left>", self.advance_image)
            self.root.bind_all("<Right>", self.advance_image)
        else:
            self.root.bind_all("<space>", self.capture_image)
        self.component_selection_panel()
        self.imgDisplay.bind("<ButtonRelease-1>", self.on_rectangle_end)
        self.imgDisplay.bind("<ButtonPress-1>", self.on_rectangle_start)
        self.imgDisplay.bind("<B1-Motion>", self.on_rectangle_drag)

    def on_rectangle_start(self, event:object) -> None:
        """
        Handle when the mouse is pressed on the image.
        """
        self.rectangleStartBounds = (event.x, event.y)
        self.imgDisplay.coords(self.rectangle, self.rectangleStartBounds[0], self.rectangleStartBounds[1], self.rectangleStartBounds[0], self.rectangleStartBounds[1])

    def on_rectangle_drag(self, event:object) -> None:
        """
        Handle when the mouse is dragged on the image.
        """
        self.rectangleEndBounds = (event.x, event.y)
        self.imgDisplay.coords(self.rectangle, self.rectangleStartBounds[0], self.rectangleStartBounds[1], self.rectangleEndBounds[0], self.rectangleEndBounds[1])

    def on_rectangle_end(self, _:object) -> None:
        """
        Handle when the mouse is released on the image.
        """
        self.saveButton.configure(state="normal")

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
            try:
                realVNCWindow = pygetwindow.getWindowsWithTitle("Component Sorter")[0]
                realVNCWindow.activate()
                pygetwindow.getWindowsWithTitle("RPi Dataset Builder")[0].activate()
            except:
                self.imgBorder.configure(bg_color=BORDER_COLOUR_FAILED)
                print("No Window Found")
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
            self.screenshot = Image.fromarray(cameraRegion)
            self.imgDisplay.image = ImageTk.PhotoImage(self.screenshot.resize(DISPLAY_IMG_SIZE, Image.NEAREST))
            self.update_image()
        else:
            self.imgBorder.configure(bg_color=BORDER_COLOUR_FAILED)
        return

    def update_image(self) -> None:
        """
        Update the image.
        """
        self.rectangleStartBounds = (0, 0)
        self.rectangleEndBounds = (0, 0)
        self.imgDisplay.coords(self.rectangle, self.rectangleStartBounds[0], self.rectangleStartBounds[1], self.rectangleEndBounds[0], self.rectangleEndBounds[1])
        self.imgDisplay.create_image(0, 0, image=self.imgDisplay.image, anchor="nw")
        self.imgDisplay.config(scrollregion=self.imgDisplay.bbox(ALL))
        self.imgDisplay.tag_raise(self.rectangle)
        self.imgBorder.configure(bg_color=BORDER_COLOUR)
        self.saveButton.configure(state="disabled")

    def save_image(self) -> None:
        """
        Save the image.
        """
        #Resistors
        if self.currentComponent == "resistors" and (len(self.selectedResistors) <= 3 or self.screenshot is None):
            return
        # Capacitors
        elif self.currentComponent == "capacitors" and (self.capacitorCapacity.get() == "" or self.capacitorVoltage.get() == "" or self.screenshot is None):
            return
        foldername = self.componentName.get().split("_")[0]
        filename = os.path.join(DATASET_PATH, foldername, 'imgs', self.componentName.get())
        num = 0
        # Make sure not to overwrite files, append a number to end
        uniqueFile = False
        while not uniqueFile:
            if os.path.isfile(os.path.join(f"{filename}_{str(num)}.png")):
                num += 1
            else:
                uniqueFile = True
        # transform the image to the correct size
        self.screenshot = self.screenshot.resize(IMG_SIZE, Image.NEAREST)
        self.screenshot.save(os.path.join(f"{filename}_{str(num)}.png"))
        # Save label.txt
        classNum = DATA[self.currentComponent]["num_label"]
        x1, y1 = self.rectangleStartBounds[0] / DISPLAY_IMG_SIZE[0], self.rectangleStartBounds[1] / DISPLAY_IMG_SIZE[1]
        x2, y2 = self.rectangleEndBounds[0] / DISPLAY_IMG_SIZE[0], self.rectangleEndBounds[1] / DISPLAY_IMG_SIZE[1]
        # Calculate center coordinates, width and height
        xCenter = (x1 + x2) / 2
        yCenter = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        with open(os.path.join(DATASET_PATH, foldername, 'labels', f"{self.componentName.get()}_{str(num)}.txt"), "w", encoding='utf-8') as f:
            f.write(f"{classNum} {round(xCenter, PRECISION)} {round(yCenter, PRECISION)} {round(width, PRECISION)} {round(height, PRECISION)}")
        # Update the save counter
        self.save_indicator()
        if self.dataSet is not None and self.dataIndex != len(self.dataSet)-1:
            self.dataIndex += 1
            self.advance_image(None)
        return

    def save_indicator(self) -> None:
        """
        Display the save indicator and flash box to indicate.
        """
        self.saveNum.set(self.saveNum.get() + 1)
        self.saveStr.set(f"Saved! x{self.saveNum.get()}")
        self.flash_box()

    def flash_box(self) -> None:
        """
        Flash the box to indicate a save.
        """
        if self.saveLabel.cget("fg_color") == "yellow":
            self.saveLabel.configure(fg_color="transparent")
        else:
            self.saveLabel.configure(fg_color="yellow")
            self.root.after(500, self.flash_box)
        return

    def advance_image(self, event:object) -> None:
        """
        Change the image.
        """
        if event is not None:
            if event.keysym == "Left" and self.dataIndex != 0:
                self.dataIndex -= 1
            elif event.keysym == "Right" and self.dataIndex != len(self.dataSet)-1:
                self.dataIndex += 1
        # Load the image
        self.screenshot = Image.open(os.path.join(self.dataPath, self.dataSet[self.dataIndex]))
        self.imgDisplay.image = ImageTk.PhotoImage(self.screenshot.resize(DISPLAY_IMG_SIZE, Image.NEAREST))
        self.filename.set(self.dataSet[self.dataIndex])
        self.update_image()
        # If label in the label file, draw the rectangle
        filename = os.path.basename(self.dataSet[self.dataIndex])
        filename = os.path.splitext(filename)[0]
        labelpath = os.path.join(self.labelPath, f"{filename}.txt")
        if os.path.isfile(labelpath):
            with open(labelpath, "r", encoding='utf-8') as f:
                label = f.readline().split(" ")
                xCenter, yCenter, width, height = float(label[1]), float(label[2]), float(label[3]), float(label[4])
                # Convert center coordinates back to top-left and bottom-right coordinates
                x1 = (xCenter - width / 2) * DISPLAY_IMG_SIZE[0]
                y1 = (yCenter - height / 2) * DISPLAY_IMG_SIZE[1]
                x2 = (xCenter + width / 2) * DISPLAY_IMG_SIZE[0]
                y2 = (yCenter + height / 2) * DISPLAY_IMG_SIZE[1]
                self.rectangleStartBounds = (x1, y1)
                self.rectangleEndBounds = (x2, y2)
                print(self.rectangleStartBounds, self.rectangleEndBounds)
                self.imgDisplay.coords(self.rectangle, self.rectangleStartBounds[0], self.rectangleStartBounds[1], self.rectangleEndBounds[0], self.rectangleEndBounds[1])
                self.imgDisplay.config(scrollregion=self.imgDisplay.bbox(ALL))
                self.imgDisplay.tag_raise(self.rectangle)
        return

    def component_selection_panel(self) -> None:
        """
        Display the component selection buttons.
        """
        self.componentSelection.grid(row=0, column=1, padx=(0, PADDING), pady=PADDING, sticky="nsew")
        self.resistorSelection.grid_remove()
        self.capacitorSelection.grid_remove()
        for _, (component, data) in enumerate(DATA.items()):
            self.root.bind(data["shortcut"], lambda _, component=component: self.component_handler(component))
        return

    def component_handler(self, component:str) -> None:
        """
        Handle when a component button is pressed or the corresponding shortcut is pressed.
        """
        self.componentName.set(DATA[component]["label"])
        self.componentSelection.grid_remove()
        self.currentComponent = component
        # Resistors
        if component == "resistors":
            for _, (colour, data) in enumerate(DATA["resistors"]["values"].items()):
                self.root.bind(data[0], lambda _, data=data, colour=colour: self.resistor_handler(colour, data))
            self.resistorSelection.grid(row=0, column=1, padx=PADDING, pady=(PADDING, 0), sticky="nsew")
            self.root.bind("<BackSpace>", lambda _: (self.selectedResistors.pop(), self.update_resistor_value()))
            self.update_resistor_value()
        else:
            for _, data in DATA["resistors"]["values"].items():
                self.root.unbind(data[0])
        # Capacitors
        if component == "capacitors":
            self.capacitorSelection.grid(row=0, column=1, padx=PADDING, pady=(PADDING, 0), sticky="nsew")
            self.root.bind("<Button-1>", lambda _: (self.update_capacitor_value()))
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
            valueDisplay += "-" + tolerance
        # If 5 band resistor or more
        elif len(self.selectedResistors) >= 5:
            valueDisplay += resistorData[self.selectedResistors[0]][1]
            valueDisplay += resistorData[self.selectedResistors[1]][1]
            valueDisplay += resistorData[self.selectedResistors[2]][1]
            value = int(valueDisplay) * 10**int(resistorData[self.selectedResistors[3]][1])
            valueDisplay += "E" + resistorData[self.selectedResistors[3]][1]
            tolerance = str(resistorData[self.selectedResistors[4]][3])
            valueDisplay += "-" + tolerance
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

    def update_capacitor_value(self) -> None:
        """
        Update the capacitor value.
        """
        componentStr = DATA["capacitors"]["label"] + "_"
        componentStr += self.capacitorCapacity.get().strip() + "F-" + self.capacitorVoltage.get().strip() + "V"
        self.componentName.set(componentStr)
        return

if __name__ == "__main__":
    main = CTk()
    obj = RPIDatasetBuilder(main)
    main.mainloop()
