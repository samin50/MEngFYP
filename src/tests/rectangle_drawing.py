# pylint: disable=all
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path)
        photo = ImageTk.PhotoImage(image)
        canvas.image = photo  # Keep a reference to avoid garbage collection
        canvas.create_image(0, 0, image=photo, anchor="nw")
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        canvas.tag_raise(rectangle)  # Raise the rectangle above the image

def on_drag_start(event):
    global start_x, start_y  # Global variables to store the start position
    start_x, start_y = event.x, event.y
    canvas.coords(rectangle, start_x, start_y, start_x, start_y)

def on_drag_motion(event):
    global start_x, start_y
    end_x, end_y = event.x, event.y
    canvas.coords(rectangle, start_x, start_y, end_x, end_y)

root = tk.Tk()

# Create a canvas
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill="both", expand=True)

# Add a rectangle, initially with no size
rectangle = canvas.create_rectangle(0, 0, 0, 0, outline="red", width=3)

# Bind the mouse events to functions
canvas.bind("<ButtonPress-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)

# Menu to open an image
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=open_image)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

root.mainloop()
