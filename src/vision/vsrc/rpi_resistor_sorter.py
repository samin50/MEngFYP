"""
Resistor Band Annotation
"""
import os
import re
from random import randint
from tkinter import Canvas
from PIL import Image, ImageTk
from customtkinter import CTk, CTkToplevel, StringVar, CTkLabel, CTkFrame
from src.vision.vsrc.constants import DISPLAY_IMG_SIZE, PADDING, DATA

class ResistorTrainer:
    def __init__(self, root:CTk, dataPath:str, labelPath:str) -> None:
        self.root = root
        self.dataPath = dataPath
        self.dataSet = os.listdir(dataPath)
        self.labelPath = labelPath
        self.dataIndex = -1
        self.colourMap = {k: i for i, (k, _) in enumerate(DATA["resistors"]["values"].items())}
        self.repattern = r'(' + '|'.join(self.colourMap.keys()) + r')'
        self.root.title("Resistor Band Annotation")
        # Variables
        self.currentFile = StringVar()
        self.colourBand = StringVar()
        self.resistorBands = []
        self.bandBoxes = []
        self.centrePoint = (0, 0)
        self.endPoint = (0, 0)
        self.mouseCoords = (0, 0)
        self.tempRect = None
        self.bandDisplay = StringVar()
        self.stemBox = None
        # Image display
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.screenshot = None
        self.imgDisplay = Canvas(self.root, width=DISPLAY_IMG_SIZE[0]//2, height=DISPLAY_IMG_SIZE[1])
        self.imgDisplay.grid(row=0, column=0, padx=PADDING, pady=PADDING)
        # UI
        CTkLabel(self.root, textvariable=self.currentFile).grid(row=1, column=0, padx=PADDING, pady=PADDING)
        CTkLabel(self.root, textvariable=self.colourBand).grid(row=2, column=0, padx=PADDING, pady=PADDING)
        CTkLabel(self.root, textvariable=self.bandDisplay).grid(row=3, column=0, padx=PADDING, pady=PADDING)
        self.textFrame = CTkFrame(self.root)
        self.textFrame.grid(row=4, column=0, padx=PADDING, pady=PADDING)
        self.saveLabel = CTkLabel(self.textFrame, text="-----")
        self.saveLabel.grid(row=4, column=0, padx=PADDING, pady=PADDING, sticky="ew")
        self.labelUpdate = CTkLabel(self.textFrame, text="---")
        self.labelUpdate.grid(row=4, column=1, padx=PADDING, pady=PADDING, sticky="ew")
        self.root.grid_columnconfigure(0, weight=1)
        self.textFrame.grid_columnconfigure(0, weight=1)
        self.textFrame.grid_columnconfigure(1, weight=1)
        # Key bindings
        self.root.bind("<a>", self.advance_image)
        self.root.bind("<d>", self.advance_image)
        self.root.bind("<ButtonPress-1>", self.start_box)
        if False: # pylint: disable=using-constant-test
            self.root.bind("<B1-Motion>", self.draw_box)
            self.root.bind("<c>", self.confirm_box)
            self.root.bind("<ButtonRelease-2>", self.cancel_box)
        else:
            self.root.bind("<ButtonPress-1>", self.draw_box_fixed)
        self.root.bind("<s>", lambda _: self.bandDisplay.set("Stem"))
        self.root.bind("<b>", lambda _: self.bandDisplay.set("Band"))
        self.root.bind("<BackSpace>", self.remove_last_box)
        self.root.bind("<Return>", self.save_label)
        self.root.bind("<x>", self.delete_specific_box)
        self.root.bind("<Motion>", self.update_mouse_coords)

    def update_mouse_coords(self, event:object) -> None:
        """
        Updates the mouse coordinates.
        """
        self.mouseCoords = (event.x, event.y)

    def advance_image(self, event:object) -> None:
        """
        Advances the image to the next one.
        """
        # Advance
        if event is not None:
            if event.keysym == "d":
                self.dataIndex += 1
            elif event.keysym == "a":
                self.dataIndex -= 1
        if self.dataIndex < 0:
            self.dataIndex = 0
            return
        elif self.dataIndex >= len(self.dataSet):
            self.dataIndex = len(self.dataSet) - 1
            return
        # Load the image
        self.screenshot = Image.open(os.path.join(self.dataPath, self.dataSet[self.dataIndex]))
        scaleFactor = self.imgDisplay.winfo_height() / self.screenshot.height
        self.imgDisplay.image = ImageTk.PhotoImage(self.screenshot.resize((int(self.screenshot.width * scaleFactor), int(self.screenshot.height * scaleFactor))))
        self.bandDisplay.set("Stem")
        self.update_image()
        # Load label if it exists
        if os.path.exists(os.path.join(self.labelPath, self.dataSet[self.dataIndex].replace(".png", ".txt"))):
            self.labelUpdate.configure(fg_color="yellow")
            self.labelUpdate.configure(text="Label Exists!")
            # Remove existing boxes
            if self.stemBox is not None:
                self.imgDisplay.delete(self.stemBox)
                self.stemBox = None
            for box in self.bandBoxes:
                self.imgDisplay.delete(box)
            self.bandBoxes = []
            with open(os.path.join(self.labelPath, self.dataSet[self.dataIndex].replace(".png", ".txt")), "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("42"):
                        # Stem
                        parts = line.split(" ")
                        xCenter, yCenter, width, height = map(float, parts[1:])
                        x1 = xCenter * self.imgDisplay.image.width() - width * self.imgDisplay.image.width() / 2
                        y1 = yCenter * self.imgDisplay.image.height() - height * self.imgDisplay.image.height() / 2
                        x2 = xCenter * self.imgDisplay.image.width() + width * self.imgDisplay.image.width() / 2
                        y2 = yCenter * self.imgDisplay.image.height() + height * self.imgDisplay.image.height() / 2
                        self.stemBox = self.imgDisplay.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
                    else:
                        # Bands
                        parts = line.split(" ")
                        xCenter, yCenter, width, height = map(float, parts[1:])
                        x1 = xCenter * self.imgDisplay.image.width() - width * self.imgDisplay.image.width() / 2
                        y1 = yCenter * self.imgDisplay.image.height() - height * self.imgDisplay.image.height() / 2
                        x2 = xCenter * self.imgDisplay.image.width() + width * self.imgDisplay.image.width() / 2
                        y2 = yCenter * self.imgDisplay.image.height() + height * self.imgDisplay.image.height() / 2
                        self.bandBoxes.append(self.imgDisplay.create_rectangle(x1, y1, x2, y2, outline="red", width=3))
            self.update_box_colours()
        else:
            self.labelUpdate.configure(fg_color="transparent")
            self.labelUpdate.configure(text="No Label Exists!")

    def update_image(self) -> None:
        """
        Updates the image display.
        """
        self.update_colour_band()
        self.bandDisplay.set("Stem")
        self.imgDisplay.create_image(0, 0, image=self.imgDisplay.image, anchor="nw", tag="screenshot")
        self.imgDisplay.tag_lower("screenshot")
        self.imgDisplay.config(scrollregion=self.imgDisplay.bbox("all"))

    def update_colour_band(self) -> None:
        """
        Updates the colour band.
        """
        self.currentFile.set(self.dataSet[self.dataIndex])
        self.resistorBands = re.findall(self.repattern, self.dataSet[self.dataIndex])
        self.colourBand.set(" ".join(self.resistorBands))
        self.imgDisplay.configure(background=DATA["resistors"]["values"][self.resistorBands[0]][2])

    def start_box(self, event:object) -> None:
        """
        Draws a box on the image.
        """
        self.centrePoint = (event.x, event.y)

    def draw_box(self, event:object) -> None:
        """
        Draws a box on the image.
        """
        width, height = event.x - self.centrePoint[0], event.y - self.centrePoint[1]
        x0, y0 = max(self.centrePoint[0] - width, 0), max(self.centrePoint[1] - height, 0)
        x1, y1 = min(self.centrePoint[0] + width, self.imgDisplay.image.width()), min(self.centrePoint[1] + height, self.imgDisplay.image.height())
        if self.tempRect is not None:
            self.imgDisplay.delete(self.tempRect)
        if self.bandDisplay.get() == "Stem":
            self.tempRect = self.imgDisplay.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)
        else:
            self.tempRect = self.imgDisplay.create_rectangle(x0, y0, x1, y1, outline="red", width=3)
        self.endPoint = (event.x, event.y)

    def draw_box_fixed(self, event:object) -> None:
        """
        Draws a box on the image with fixed size.
        """
        width, height = randint(90, 110), randint(30, 40)
        if self.bandDisplay.get() == "Stem":
            width, height = randint(110, 130), randint(60, 100)
        x0, y0 = max(event.x - width, 0), max(event.y - height, 0)
        x1, y1 = min(event.x + width, self.imgDisplay.image.width()), min(event.y + height, self.imgDisplay.image.height())
        if self.bandDisplay.get() == "Stem":
            if self.stemBox is not None:
                self.imgDisplay.delete(self.stemBox)
            self.stemBox = self.imgDisplay.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)
            self.bandDisplay.set("Band")
        elif len(self.bandBoxes) <= 5:
            self.bandBoxes.append(self.imgDisplay.create_rectangle(x0, y0, x1, y1, outline="red", width=3))
        self.update_box_colours()

    def cancel_box(self, _:object) -> None:
        """
        Cancels the box.
        """
        if self.tempRect is not None:
            self.imgDisplay.delete(self.tempRect)
            self.tempRect = None

    def confirm_box(self, _:object) -> None:
        """
        Confirms the box.
        """
        if self.tempRect is not None and len(self.bandBoxes) < 5:
            width, height = self.endPoint[0] - self.centrePoint[0], self.endPoint[1] - self.centrePoint[1]
            self.imgDisplay.delete(self.tempRect)
            self.tempRect = None
            if self.bandDisplay.get() == "Stem":
                if self.stemBox is not None:
                    self.imgDisplay.delete(self.stemBox)
                    self.stemBox = None
                self.stemBox = self.imgDisplay.create_rectangle(self.centrePoint[0] - width, self.centrePoint[1] - height, self.centrePoint[0] + width, \
                                                 self.centrePoint[1] + height, outline="yellow", width=3)
                self.bandDisplay.set("Band")
            else:
                self.bandBoxes.append(self.imgDisplay.create_rectangle(self.centrePoint[0] - width, self.centrePoint[1] - height, self.centrePoint[0] + width, \
                                             self.centrePoint[1] + height, outline="red", width=3))

    def remove_last_box(self, _:object) -> None:
        """
        Removes the last box.
        """
        if len(self.bandBoxes) > 0:
            self.imgDisplay.delete(self.bandBoxes.pop())

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

    def flash_label(self) -> None:
        """
        Flash the box to indicate a save.
        """
        if self.labelUpdate.cget("fg_color") == "yellow":
            self.labelUpdate.configure(fg_color="transparent")
        else:
            self.labelUpdate.configure(fg_color="yellow")
            self.root.after(500, self.flash_label)
        return

    def save_label(self, _:object) -> None:
        """
        Saves the label.
        """
        if len(self.bandBoxes) >= 4:
            # Save the label
            label = [self.colourMap[band] for band in self.resistorBands] #42 is stem label
            # Determine whether stem is at the top or bottom
            stemBox = self.imgDisplay.coords(self.stemBox)
            #Determine average y value of other resistor bands
            avgY = 0
            for box in self.bandBoxes:
                avgY += self.imgDisplay.coords(box)[1]
            avgY /= 5
            # If the stem is below the average y value, then it is at the bottom
            reverse = stemBox[1] > avgY
            # Determine coords of resistor bands according to yolov8 format
            coords = []
            for box in self.bandBoxes:
                boxCoords = self.imgDisplay.coords(box)
                xCenter = (boxCoords[0] + boxCoords[2]) / (2 * self.imgDisplay.image.width())
                yCenter = (boxCoords[1] + boxCoords[3]) / (2 * self.imgDisplay.image.height())
                width = (boxCoords[2] - boxCoords[0]) / self.imgDisplay.image.width()
                height = (boxCoords[3] - boxCoords[1]) / self.imgDisplay.image.height()
                coords.append((xCenter, yCenter, width, height))
            # Assign label to resistor bands with the one closest to the stem being the first band
            coords.sort(key=lambda x: x[1]) # sort by yCenter
            finalLabel = []
            # Add stem label
            stemCoords = self.imgDisplay.coords(self.stemBox)
            xCenter = (stemCoords[0] + stemCoords[2]) / (2 * self.imgDisplay.image.width())
            yCenter = (stemCoords[1] + stemCoords[3]) / (2 * self.imgDisplay.image.height())
            width = (stemCoords[2] - stemCoords[0]) / self.imgDisplay.image.width()
            height = (stemCoords[3] - stemCoords[1]) / self.imgDisplay.image.height()
            finalLabel.append(f"42 {xCenter} {yCenter} {width} {height}")
            if reverse:
                finalLabel += [f"{label[i]} {x[0]} {x[1]} {x[2]} {x[3]}" for i, x in enumerate(coords[::-1])]
            else:
                finalLabel += [f"{label[i]} {x[0]} {x[1]} {x[2]} {x[3]}" for i, x in enumerate(coords)]
            # Save the label
            with open(os.path.join(self.labelPath, self.dataSet[self.dataIndex].replace(".png", ".txt")), "w", encoding="utf-8") as f:
                f.write("\n".join(finalLabel))
            self.saveLabel.configure(text="Saved")
            self.flash_box()
        else:
            self.saveLabel.configure(text="Not enough bands")

    def delete_specific_box(self, _:object) -> None:
        """
        Delete the box the mouse is hovering inside
        """
        print(self.mouseCoords)
        for i, box in enumerate(self.bandBoxes):
            boxCoords = self.imgDisplay.coords(box)
            print(boxCoords)
            if boxCoords[0] < self.mouseCoords[0] < boxCoords[2] and boxCoords[1] < self.mouseCoords[1] < boxCoords[3]:
                self.imgDisplay.delete(box)
                self.bandBoxes.pop(i)
                return

    def update_box_colours(self) -> None:
        """
        Updates the boxes with the colour band.
        """
        # Sort the boxes by y-coordinate
        self.bandBoxes.sort(key=lambda x: self.imgDisplay.coords(x)[1])
        # Reverse the boxes if the stem is at the top
        if self.stemBox is not None:
            stemCoords = self.imgDisplay.coords(self.stemBox)
            if stemCoords[1] > sum(self.imgDisplay.coords(box)[1] for box in self.bandBoxes) / 5:
                self.bandBoxes = self.bandBoxes[::-1]
        # Update the boxes
        for i, box in enumerate(self.bandBoxes):
            self.imgDisplay.itemconfig(box, outline=DATA["resistors"]["values"][self.resistorBands[i]][2])


if __name__ == "__main__":
    main = CTk()
    ResistorTrainer(CTkToplevel(main), "./src/vision/datasets/partial/resistor/imgs", "./src/vision/datasets/partial/resistor/labels")
    main.mainloop()
