"""
Handy frontend tool for training the vision model.
"""
from customtkinter import CTk, CTkToplevel, CTkButton
from src.vision.vsrc.rpi_dataset_builder import RPIDatasetBuilder
from src.vision.vsrc.constants import TITLE, RESOLUTION, PADDING

class VisionTrainer:
    def __init__(self, root:CTk) -> None:
        self.root = root
        self.root.title(TITLE)
        self.root.geometry(RESOLUTION)
        # Grid weights
        self.root.grid_columnconfigure(0, weight=1)
        # Setup widgets
        CTkButton(self.root, text="Open RPi Dataset Builder", command=self.rpi_dataset_builder).grid(row=0, column=0, padx=PADDING, pady=PADDING, sticky="nsew")

    def rpi_dataset_builder(self) -> None:
        """
        Opens the RPi Dataset Builder.
        Uses RealVNC to capture the screen of the Raspberry Pi.
        """
        RPIDatasetBuilder(CTkToplevel(self.root))

if __name__ == "__main__":
    main = CTk()
    obj = RPIDatasetBuilder(main)
    main.mainloop()
