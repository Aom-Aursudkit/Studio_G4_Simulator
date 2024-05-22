import pygame
import pygame_gui
import sys
import math

# Initialize Pygame and pygame_gui
pygame.init()
pygame.display.set_caption('Interactive Circle in Triangle')

# Screen dimensions and colors
width, height = 1600, 900
screen = pygame.display.set_mode((width, height))
background_color = (30, 30, 30)  # Dark gray
triangle_color = (60, 180, 75)   # Soft green
circle_color = (255, 165, 0)     # Orange

# Equilateral triangle specifications
side_length = 500
triangle_height = (math.sqrt(3) / 2) * side_length
horizontal_margin = (width - side_length) / 2
vertical_margin = (height - triangle_height) / 2

# Triangle vertices
vertex1 = (width // 2, int(vertical_margin))
vertex2 = (int(horizontal_margin), int(height - vertical_margin))
vertex3 = (int(width - horizontal_margin), int(height - vertical_margin))

# Circle
circle_radius = 70
circle_x, circle_y = vertex1[0], height - (vertex1[1] + circle_radius)

# GUI Manager for pygame_gui
manager = pygame_gui.UIManager((width, height), "data/themes/theme.json")

# Slider for x-coordinate
x_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 750), (360, 50)),
    start_value=circle_x,
    value_range=(vertex2[0] + circle_radius, vertex3[0] - circle_radius),
    manager=manager)

# Text box for x-coordinate
x_text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((400, 750), (380, 50)),
    manager=manager)
x_text_entry.set_text(str(circle_x))

# Slider for y-coordinate with inverted values
y_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 700), (360, 50)),
    start_value=height - circle_y,
    value_range=(height - (vertex1[1] + circle_radius), height - (vertex2[1] - circle_radius)),  # Adjust this range based on actual limits
    manager=manager
)

# Text box for y-coordinate
y_text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((400, 700), (380, 50)),
    manager=manager)
y_text_entry.set_text(str(height - circle_y))

def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

def point_in_triangle(px, py, v1, v2, v3):
    b1 = sign((px, py), v1, v2) < 0.0
    b2 = sign((px, py), v2, v3) < 0.0
    b3 = sign((px, py), v3, v1) < 0.0
    return ((b1 == b2) and (b2 == b3))

def circle_in_triangle(cx, cy, rad, v1, v2, v3):
    for angle in range(0, 360, 1):  # Check every 1 degrees
        px = cx + rad * math.cos(math.radians(angle))
        py = cy + rad * math.sin(math.radians(angle))
        if not point_in_triangle(px, py, v1, v2, v3):
            return False
    return True

# Game loop with visual enhancements
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == x_slider:
                    test_x = event.value
                    if circle_in_triangle(test_x, circle_y, circle_radius, vertex1, vertex2, vertex3):
                        circle_x = test_x
                    x_text_entry.set_text(str(int(circle_x)))
                elif event.ui_element == y_slider:
                    test_y = height - event.value  # Invert the slider value for actual y-coordinate
                    if circle_in_triangle(circle_x, test_y, circle_radius, vertex1, vertex2, vertex3):
                        circle_y = test_y
                    y_text_entry.set_text(str(height - int(circle_y)))  # Reflect inverted y in text entry
            elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == x_text_entry:
                    try:
                        test_x = int(x_text_entry.get_text())
                        if circle_in_triangle(test_x, circle_y, circle_radius, vertex1, vertex2, vertex3):
                            circle_x = test_x
                            x_slider.set_current_value(circle_x)
                    except ValueError:
                        x_text_entry.set_text(str(int(circle_x)))
                elif event.ui_element == y_text_entry:
                    try:
                        test_y = height - int(y_text_entry.get_text())  # Invert the input from the text box
                        if circle_in_triangle(circle_x, test_y, circle_radius, vertex1, vertex2, vertex3):
                            circle_y = test_y
                            y_slider.set_current_value(height - circle_y)
                    except ValueError:
                        y_text_entry.set_text(str(height - int(circle_y)))
        
        manager.process_events(event)
    
    manager.update(time_delta)

    # Fill the screen with a nicer background color
    screen.fill(background_color)

    # Draw the triangle with a nicer color
    pygame.draw.polygon(screen, triangle_color, [vertex1, vertex2, vertex3])

    # Draw the circle
    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

    manager.draw_ui(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()