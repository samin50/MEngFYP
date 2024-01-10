# pylint: disable=all
# Importing necessary libraries
import pygame
import pygame_gui
import random

# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Frame Rate Adjuster")

# Setting up pygame_gui
manager = pygame_gui.UIManager((screen_width, screen_height))
clock = pygame.time.Clock()

# GUI manager clock (for smoother GUI updates)
gui_clock = pygame.time.Clock()
gui_update_interval = 60  # GUI updates per second

# Variables for the moving circle
circle_color = (255, 0, 0)  # Red color
circle_radius = 20
circle_x = random.randint(circle_radius, screen_width - circle_radius)
circle_y = random.randint(circle_radius, screen_height - circle_radius)
circle_speed_x = 500
circle_speed_y = 500

# Frame rate variables
frame_rate = 30
frame_rate_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (140, 25)),
                                               text=f"Frame rate: {frame_rate}",
                                               manager=manager)
frame_rate_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((160, 10), (200, 25)),
                                                           start_value=frame_rate,
                                                           value_range=(1, 120),
                                                           manager=manager)
ball_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 40), (140, 25)),
                                               text=f"Ball speed: {circle_speed_x}",
                                               manager=manager)
ball_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((160, 40), (200, 25)),
                                                           start_value=circle_speed_x,
                                                           value_range=(100, 1000),
                                                           manager=manager)

# Main loop
running = True
while running:
    time_delta = clock.tick(frame_rate) / 1000.0
    manager_delta = gui_clock.tick(gui_update_interval) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == frame_rate_slider:
                frame_rate = int(frame_rate_slider.get_current_value())
                frame_rate_label.set_text(f"Frame rate: {frame_rate}")
            elif event.ui_element == ball_speed_slider:
                circle_speed_x = int(ball_speed_slider.get_current_value())
                circle_speed_y = int(ball_speed_slider.get_current_value())
                ball_speed_label.set_text(f"Ball speed: {circle_speed_x}")
    # Moving the circle
    circle_x += circle_speed_x * time_delta
    circle_y += circle_speed_y * time_delta

    # Bouncing the circle off the edges
    if circle_x <= circle_radius or circle_x >= screen_width - circle_radius:
        circle_speed_x *= -1
        circle_x = max(circle_radius, min(circle_x, screen_width - circle_radius))
    if circle_y <= circle_radius or circle_y >= screen_height - circle_radius:
        circle_speed_y *= -1
        circle_y = max(circle_radius, min(circle_y, screen_height - circle_radius))

    # Updating the screen
    screen.fill((0, 0, 0))  # Black background
    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)
    manager.update(manager_delta)
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
