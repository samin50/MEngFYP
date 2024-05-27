"""
Handy frontend tool for training the vision model.
"""
from customtkinter import CTk, CTkToplevel, CTkButton, filedialog
from src.vision.vsrc.rpi_dataset_builder import RPIDatasetBuilder
from src.vision.vsrc.rpi_resistor_sorter import ResistorTrainer
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
        CTkButton(self.root, text="Open Dataset Sorter", command=self.dataset_sorter).grid(row=1, column=0, padx=PADDING, pady=PADDING, sticky="nsew")
        CTkButton(self.root, text="Open Resistor Band Annotation", command=self.resistor_trainer).grid(row=2, column=0, padx=PADDING, pady=PADDING, sticky="nsew")

    def rpi_dataset_builder(self) -> None:
        """
        Opens the RPi Dataset Builder.
        Uses RealVNC to capture the screen of the Raspberry Pi.
        """
        RPIDatasetBuilder(CTkToplevel(self.root))

    def dataset_sorter(self) -> None:
        """
        Opens the Dataset Sorter.
        """
        datapath = filedialog.askdirectory(
            title="Select the dataset folder to sort.",
            initialdir="./src/vision/datasets"
        )
        if datapath == "":
            return
        labelpath = filedialog.askdirectory(
            title="Select the folder to save labels to.",
            initialdir="./src/vision/datasets"
        )
        if labelpath == "":
            return
        RPIDatasetBuilder(CTkToplevel(self.root), datapath, labelpath)

    def resistor_trainer(self) -> None:
        """
        Opens the Resistor Band Annotation.
        """
        datapath = filedialog.askdirectory(
            title="Select the dataset folder to sort.",
            initialdir="./src/vision/datasets/partial/resistor"
        )
        if datapath == "":
            return
        labelpath = filedialog.askdirectory(
            title="Select the folder to save labels to.",
            initialdir="./src/vision/datasets/partial/resistor"
        )
        if labelpath == "":
            return
        ResistorTrainer(CTkToplevel(self.root), datapath, labelpath)

if __name__ == "__main__":
    main = CTk()
    obj = VisionTrainer(main)
    main.mainloop()
