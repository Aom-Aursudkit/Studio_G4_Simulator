import pygame
import pygame_gui
import numpy as np
import sys
from scipy.optimize import minimize
import math

# -projectile-#\/################################################

# Constants
g = 9.81  # m/s^2, acceleration due to gravity
target_x = 2.00  # meters
wall_x = 1.00  # meters
wall_y = 0.60  # meters
theta = 45  # angle in degrees

h = 0.3
target_z = 250
target_y = 0.755 + 0.007

# -pygame-#\/###################################################

# Initialize Pygame and pygame_gui
pygame.init()
pygame.display.set_caption("Projectile Simulator")
state = "menu"

# Screen dimensions and colors
width, height = 1600, 900
screen = pygame.display.set_mode((width, height))

# Colors
BLACK = (0, 0, 0)
WHITE = (217, 217, 217)
RED = (209, 106, 106)
GREEN = (0, 255, 102)
DARKER_GREEN = (0, 200, 0)
LIGHT_BLUE = (172, 230, 255)
BLUE = (122, 180, 205)
background_color = (30, 30, 30)  # Dark gray

font = pygame.font.Font(None, 36)

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
circle_radius = 69
circle_z, circle_y = vertex1[0], height - (vertex1[1] + circle_radius)

# animating
point_index = 0
animating = False
time_elapsed = 0

# image
side_view = pygame.image.load(
    "data/images/side_view_2024-05-21_151130-removebg-preview.png"
)
side_view = pygame.transform.scale(side_view, ((0.27 * 460 * 536) / 466, 0.27 * 460))

# GUI Manager for pygame_gui
manager = pygame_gui.UIManager((width, height))

# GUI Elements ###################################################
# Text box for y-coordinate
y_text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((730, 700), (150, 50)), manager=manager
)
y_text_entry.set_text(str(70))

# Text box for z-coordinate
z_text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((730, 750), (150, 50)), manager=manager
)
z_text_entry.set_text(str(250))
##################################################################


# Target #########################################################
def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def point_in_triangle(pz, py, v1, v2, v3):
    b1 = sign((pz, py), v1, v2) < 0.0
    b2 = sign((pz, py), v2, v3) < 0.0
    b3 = sign((pz, py), v3, v1) < 0.0
    return (b1 == b2) and (b2 == b3)


def circle_in_triangle(cz, cy, rad, v1, v2, v3):
    for angle in range(0, 360, 1):  # Check every 1 degrees
        pz = cz + rad * math.cos(math.radians(angle))
        py = cy + rad * math.sin(math.radians(angle))
        if not point_in_triangle(pz, py, v1, v2, v3):
            return False
    return True


temp_y = 70
test_y = height - vertical_margin - temp_y
circle_y = test_y
target_y = (temp_y / 1000) + 0.755

temp_z = 250
test_z = int(horizontal_margin) + temp_z
circle_z = test_z
target_z = temp_z / 10

# -projectile-#\/################################################


# Function to calculate the position of the projectile
def projectile_motion(v0, theta):
    theta_rad = np.radians(theta)
    # Time when projectile is at target_x
    time_to_target_x = target_x / (v0 * np.cos(theta_rad))
    # Position calculation
    x = v0 * np.cos(theta_rad) * time_to_target_x
    y = h + v0 * np.sin(theta_rad) * time_to_target_x - 0.5 * g * time_to_target_x**2
    return x, y


# Function to calculate y position at wall_x given v0 and theta
def y_at_wall(v0, theta):
    theta_rad = np.radians(theta)
    time_to_wall_x = wall_x / (v0 * np.cos(theta_rad))
    y_wall = h + v0 * np.sin(theta_rad) * time_to_wall_x - 0.5 * g * time_to_wall_x**2
    return y_wall


# Optimization function that adjusts v0 for a given theta to hit the target
def optimize_v0(theta):
    # Objective: Minimize the difference in y from the target at target_x
    def objective(v0):
        _, y = projectile_motion(v0[0], theta)
        return abs(target_y - y)

    # Constraint: Projectile must clear the wall
    def constraint(v0):
        return y_at_wall(v0[0], theta) - wall_y

    # Initial guess for v0
    initial_guess = [10]
    # Bounds for v0
    bounds = [(1, 100)]
    # Constraint
    cons = [{"type": "ineq", "fun": constraint}]

    # Run optimization
    result = minimize(
        objective, initial_guess, method="SLSQP", bounds=bounds, constraints=cons
    )
    return result.x[0]


# Find optimized v0 for the given theta
v0_optimized = optimize_v0(theta)


# Generate trajectory
def trajectory(v0, theta, num_points=1000):
    theta_rad = np.radians(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / g
    t = np.linspace(0, t_max, num_points)
    x = v0 * np.cos(theta_rad) * t
    y = h + v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    return x, y


def trajec_animating(v0, theta, num_points=1000):
    theta_rad = np.radians(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / g
    t_intervals = [t_max * i / num_points for i in range(num_points + 1)]
    t = np.linspace(0, t_max, num_points)
    x = v0 * np.cos(theta_rad) * t
    y = h + v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    return x, y, t_intervals


x_trajectory, y_trajectory = trajectory(v0_optimized, theta)

##--state--##############################
clock = pygame.time.Clock()


def menu():
    global state, circle_z, circle_y, clock, target_y, target_z, animating, point_index, time_elapsed
    button_rect = pygame.Rect(50, 50, 200, 50)
    text_start = font.render("Calculate", True, BLACK)
    text_start_rect = text_start.get_rect(center=button_rect.center)
    animating = False
    point_index = 0
    time_elapsed = 0

    menu_running = True
    while menu_running and state == "menu":
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    state = "play"
                    menu_running = False

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == y_text_entry:
                    try:
                        temp_y = int(y_text_entry.get_text())
                        test_y = height - vertical_margin - temp_y
                        target_y = (temp_y / 1000) + 0.755
                        if circle_in_triangle(
                            circle_z, test_y, circle_radius, vertex1, vertex2, vertex3
                        ):
                            circle_y = test_y
                    except ValueError:
                        y_text_entry.set_text(
                            str(int(height - vertical_margin - circle_y))
                        )
                elif event.ui_element == z_text_entry:
                    try:
                        temp_z = int(z_text_entry.get_text())
                        test_z = int(horizontal_margin) + temp_z
                        target_z = temp_z / 10
                        if circle_in_triangle(
                            test_z, circle_y, circle_radius, vertex1, vertex2, vertex3
                        ):
                            circle_z = test_z
                    except ValueError:
                        z_text_entry.set_text(str(int(circle_z - horizontal_margin)))

            manager.process_events(event)

        manager.update(time_delta)

        # Fill the screen with a nicer background color
        screen.fill(background_color)

        # Draw the triangle with a nicer color
        pygame.draw.polygon(screen, WHITE, [vertex1, vertex2, vertex3])

        # Draw the circle
        pygame.draw.circle(
            screen, background_color, (circle_z, circle_y), circle_radius
        )

        manager.draw_ui(screen)

        mouse_pos = pygame.mouse.get_pos()
        current_color = BLUE if button_rect.collidepoint(mouse_pos) else LIGHT_BLUE
        pygame.draw.rect(screen, current_color, button_rect)
        screen.blit(text_start, text_start_rect)

        text = font.render("Target Y", True, WHITE)
        screen.blit(text, (620, 715))
        text = font.render("mm", True, WHITE)
        screen.blit(text, (890, 715))
        text = font.render("Target Z", True, WHITE)
        screen.blit(text, (620, 765))
        text = font.render("mm", True, WHITE)
        screen.blit(text, (890, 765))

        # Update the display
        pygame.display.flip()


def draw():
    global h, target_y, v0_optimized, state, back_button_rect, start_stop_button_rect, reset_button_rect, point_index, time_elapsed, side_view

    screen.fill(background_color)

    # button
    back_button_rect = pygame.Rect(50, 50, 200, 50)
    back_text = font.render("Go back", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)

    start_stop_button_rect = pygame.Rect(50, 110, 200, 50)
    start_stop_text = font.render("Start/Stop", True, BLACK)
    start_stop_text_rect = start_stop_text.get_rect(
        center=start_stop_button_rect.center
    )

    reset_button_rect = pygame.Rect(260, 110, 200, 50)
    reset_text = font.render("Reset", True, BLACK)
    reset_text_rect = reset_text.get_rect(center=reset_button_rect.center)

    mouse_pos = pygame.mouse.get_pos()
    back_color = BLUE if back_button_rect.collidepoint(mouse_pos) else LIGHT_BLUE
    pygame.draw.rect(screen, back_color, back_button_rect)
    screen.blit(back_text, back_text_rect)

    start_stop_color = (
        BLUE if start_stop_button_rect.collidepoint(mouse_pos) else LIGHT_BLUE
    )
    pygame.draw.rect(screen, start_stop_color, start_stop_button_rect)
    screen.blit(start_stop_text, start_stop_text_rect)

    reset_color = BLUE if reset_button_rect.collidepoint(mouse_pos) else LIGHT_BLUE
    pygame.draw.rect(screen, reset_color, reset_button_rect)
    screen.blit(reset_text, reset_text_rect)

    # vert coordinates to pixels
    scale = 460  # pixels per meter
    origin_x = 300
    origin_y = height - 70

    # Draw target
    target_pos = (origin_x + scale * target_x, origin_y - scale * target_y)
    pygame.draw.line(
        screen,
        WHITE,
        (target_pos[0], origin_y),
        (target_pos[0], origin_y - scale * 0.755),
        10,
    )
    pygame.draw.line(
        screen,
        BLUE,
        (target_pos[0], origin_y - (scale * 0.755)),
        (target_pos[0], origin_y - (scale * 0.755) - (scale * triangle_height / 1000)),
        10,
    )
    pygame.draw.line(
        screen,
        RED,
        (target_pos[0], target_pos[1] + scale * 0.07),
        (target_pos[0], target_pos[1] - scale * 0.07),
        10,
    )
    # pygame.draw.circle(screen, RED, target_pos, scale * 0.07)

    # Draw wall
    wall_pos_x = origin_x + scale * wall_x
    wall_top_y = origin_y - scale * wall_y
    pygame.draw.line(
        screen, WHITE, (wall_pos_x, origin_y), (wall_pos_x, wall_top_y), 10
    )

    # Draw scale
    for y in range(origin_y, int(origin_y - (scale * 1.4)) + 1, -23):
        pygame.draw.line(screen, WHITE, (origin_x - 150, y), (origin_x - 160, y), 1)
    pygame.draw.line(screen, WHITE, (origin_x - 160, origin_y + 5), (target_pos[0] + 5, origin_y + 5), 10)
    for x in range(origin_x, int(target_pos[0]) + 1, 23):
        pygame.draw.line(screen, WHITE, (x, origin_y + 10), (x, origin_y + 20), 1)

    # import image
    screen.blit(
        side_view, (origin_x - (0.27 * scale * 536) / 466, origin_y - 0.27 * scale)
    )

    # Display output
    text = font.render(f"Optimized v0: {v0_optimized:.4f} m/s", True, WHITE)
    screen.blit(text, (300, 50))
    text_pos_z = font.render(
        f"Z position from the left side: {target_z} cm", True, WHITE
    )
    screen.blit(text_pos_z, (750, 50))

    # Draw trajectory
    x_traj, y_traj = trajectory(v0_optimized, theta, num_points=100)
    points = [
        (origin_x + scale * x, origin_y - scale * y)
        for x, y in zip(x_traj, y_traj)
        if y >= 0
    ]
    if points:
        pygame.draw.lines(screen, WHITE, False, points, 2)

    # animating trajectory
    x_traj, y_traj, t_intervals = trajec_animating(v0_optimized, theta, num_points=100)
    points = [
        (origin_x + scale * x, origin_y - scale * y)
        for x, y in zip(x_traj, y_traj)
        if y >= 0
    ]
    if animating and point_index < len(points):
        time_elapsed += clock.get_time() / 1000  # Time in seconds
        while (
            point_index < len(points) - 1 and time_elapsed >= t_intervals[point_index]
        ):
            point_index += 1
        if point_index < len(points):
            ball_pos = points[point_index]
            pygame.draw.circle(screen, RED, ball_pos, 0.02 * scale)
    elif not animating and point_index > 0:
        ball_pos = points[point_index]
        pygame.draw.circle(screen, RED, ball_pos, 0.02 * scale)

    pygame.display.flip()


def event():
    global h, target_y, v0_optimized, state, animating, point_index, time_elapsed
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_button_rect.collidepoint(event.pos):
                state = "menu"
            if start_stop_button_rect.collidepoint(event.pos):
                animating = not animating
            if reset_button_rect.collidepoint(event.pos):
                animating = False
                point_index = 0
                time_elapsed = 0
        v0_optimized = optimize_v0(
            theta
        )  # Update the velocity each time the input changes
        manager.process_events(event)
    manager.update(time_delta)


while True:
    if state == "menu":
        menu()
    elif state == "play":
        while state == "play":
            draw()
            event()
            # print(v0_optimized)
    pygame.display.flip()
