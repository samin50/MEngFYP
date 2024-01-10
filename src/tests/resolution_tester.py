# pylint: disable=all
import tkinter.filedialog as filedialog
import os
import pygame
import pygame_gui

# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image Scaler")

# Setting up pygame_gui
manager = pygame_gui.UIManager((screen_width, screen_height))

# Load an initial image
imagefolder = './src/vision/dataset/'
initial_image_path = imagefolder + 'test.png'  # Replace with a default image path
if os.path.exists(initial_image_path):
    original_image = pygame.image.load(initial_image_path)
else:
    original_image = pygame.Surface((100, 100))  # Default blank surface if image not found

# Display size of the image
display_size = (708, 528)  # Size at which the image will be displayed

def scale_image(img, resolution):
    # Calculate aspect ratio
    width, height = img.get_size()
    aspect_ratio = width / height

    # Scale to the new resolution while maintaining aspect ratio
    if aspect_ratio > 1:
        new_width = resolution
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = resolution
        new_width = int(new_height * aspect_ratio)

    scaled_img = pygame.transform.scale(img, (new_width, new_height))

    # Scale back to the display size
    return pygame.transform.scale(scaled_img, display_size)



# Initially scale the image
image = scale_image(original_image, 100)

# GUI elements
resolution_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 40), (200, 25)),
                                                           start_value=100,
                                                           value_range=(50, 500),
                                                           manager=manager)
resolution_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (200, 25)),
                                               text=f"Resolution: 100",
                                               manager=manager)
open_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((220, 40), (100, 25)),
                                           text='Open Image',
                                           manager=manager)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    time_delta = clock.tick(60) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == resolution_slider:
                    new_resolution = int(resolution_slider.get_current_value())
                    image = scale_image(original_image, new_resolution)
                    resolution_label.set_text(f"Resolution: {new_resolution}")

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == open_button:
                    # Implement a file picker to open image
                    # Note: You'll need to integrate an external library or custom solution for file picker
                    filepath = filedialog.askopenfilename(initialdir=imagefolder, title="Select Image",
                                                          filetypes=((".png files", "*.png"), ("all files", "*.*")))
                    if filepath != "":
                        original_image = pygame.image.load(filepath)
                        # Scale image to match slider value
                        new_resolution = int(resolution_slider.get_current_value())
                        image = scale_image(original_image, new_resolution)
                        resolution_label.set_text(f"Resolution: {new_resolution}")
                        display_size = (image.get_width(), image.get_height())

        manager.process_events(event)

    # Update GUI
    manager.update(time_delta)

    # Drawing
    screen.fill((0, 0, 0))
    screen.blit(image, image.get_rect(center=screen.get_rect().center))
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
