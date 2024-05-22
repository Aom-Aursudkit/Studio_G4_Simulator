import pygame
import pygame_gui
import numpy as np
import sys
from scipy.optimize import minimize
# import matplotlib.pyplot as plt

#-projectile-#\/################################################

# Constants
g = 9.81  # m/s^2, acceleration due to gravity
target_x = 2.00  # meters
wall_x = 1.00  # meters
wall_y = 0.60  # meters
theta = 45  # angle in degrees

# Initial parameters
h = 0.3226  # initial height (meters)
target_y = 1.24  # target height (meters)

#-pygame-#\/###################################################

# Pygame and pygame_gui setup
pygame.init()
pygame.display.set_caption("Projectile Simulator")
width, height = 1600, 900
screen = pygame.display.set_mode((width, height))
manager = pygame_gui.UIManager((width, height))
state = "menu"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKER_GREEN = (0, 200, 0)

font = pygame.font.Font(None, 36)

# GUI Elements
initial_height_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 800), (300, 50)),
    start_value=h,
    value_range=(0.1, 0.6),
    manager=manager,
    object_id='initial_height_slider')

initial_height_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((400, 800), (100, 50)),
    manager=manager,
    object_id='initial_height_entry')
initial_height_entry.set_text(str(h))

target_height_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 850), (300, 50)),
    start_value=target_y,
    value_range=(1.0, 1.3),
    manager=manager,
    object_id='target_height_slider')

target_height_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((400, 850), (100, 50)),
    manager=manager,
    object_id='target_height_entry')
target_height_entry.set_text(str(target_y))

#-projectile-#\/################################################

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
    cons = [{'type': 'ineq', 'fun': constraint}]
    
    # Run optimization
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=cons)
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

x_trajectory, y_trajectory = trajectory(v0_optimized, theta)
print(v0_optimized)

#-pygame-#\/###################################################

def menu():
    global state
    button_rect = pygame.Rect(100, 100, 200, 50)
    text = font.render('Start', True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    
    menu_running = True
    while menu_running and state == "menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    state = "play"
                    menu_running = False
            
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        current_color = DARKER_GREEN if button_rect.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(screen, current_color, button_rect)
        screen.blit(text, text_rect)
        pygame.display.flip()

def draw():
    global h, target_y, v0_optimized, state, back_button_rect

    back_button_rect = pygame.Rect(50, 50, 100, 50)
    back_text = font.render('Menu', True, WHITE)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    
    # while state == "play":
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
    #         elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #             if back_button_rect.collidepoint(event.pos):
    #                 state = "menu"
    #         elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
    #             if event.ui_object_id == 'initial_height_slider':
    #                 h = event.value
    #                 initial_height_entry.set_text(str(round(h, 4)))
    #             elif event.ui_object_id == 'target_height_slider':
    #                 target_y = event.value
    #                 target_height_entry.set_text(str(round(target_y, 4)))
    #         elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
    #             if event.ui_object_id == 'initial_height_entry':
    #                 h = float(event.text)
    #                 initial_height_slider.set_current_value(h)
    #             elif event.ui_object_id == 'target_height_entry':
    #                 target_y = float(event.text)
    #                 target_height_slider.set_current_value(target_y)
    #         v0_optimized = optimize_v0(theta)  # Update the velocity each time the input changes
    #         manager.process_events(event)
    #     manager.update(time_delta)

    screen.fill(BLACK)
    manager.draw_ui(screen)
    text = font.render(f'Initial height', True, WHITE)
    screen.blit(text, (505, 810))
    text = font.render(f'Target height', True, WHITE)
    screen.blit(text, (505, 860))
    
    mouse_pos = pygame.mouse.get_pos()
    back_color = DARKER_GREEN if back_button_rect.collidepoint(mouse_pos) else GREEN
    pygame.draw.rect(screen, back_color, back_button_rect)
    screen.blit(back_text, back_text_rect)
    
    # vert coordinates to pixels
    scale = 400  # pixels per meter
    origin_x = 50
    origin_y = height - 120
    
    # Draw trajectory
    x_traj, y_traj = trajectory(v0_optimized, theta, num_points=100)
    points = [(origin_x + scale * x, origin_y - scale * y) for x, y in zip(x_traj, y_traj) if y >= 0]
    if points:
        pygame.draw.lines(screen, WHITE, False, points, 2)
    
    # Draw target
    target_pos = (origin_x + scale * target_x, origin_y - scale * target_y)
    pygame.draw.circle(screen, RED, target_pos, 10)

    # Draw wall
    wall_pos_x = origin_x + scale * wall_x
    wall_top_y = origin_y - scale * wall_y
    pygame.draw.line(screen, GREEN, (wall_pos_x, origin_y), (wall_pos_x, wall_top_y), 5)

    # Display v0
    text = font.render(f'Optimized v0: {v0_optimized:.4f} m/s', True, WHITE)
    screen.blit(text, (300, 50))
    
    pygame.display.flip()

def event():
    global h, target_y, v0_optimized, state
    time_delta = clock.tick(60)/1000.0
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_button_rect.collidepoint(event.pos):
                state = "menu"
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_object_id == 'initial_height_slider':
                h = event.value
                initial_height_entry.set_text(str(round(h, 4)))
            elif event.ui_object_id == 'target_height_slider':
                target_y = event.value
                target_height_entry.set_text(str(round(target_y, 4)))
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_object_id == 'initial_height_entry':
                h = float(event.text)
                initial_height_slider.set_current_value(h)
            elif event.ui_object_id == 'target_height_entry':
                target_y = float(event.text)
                target_height_slider.set_current_value(target_y)
        v0_optimized = optimize_v0(theta)  # Update the velocity each time the input changes
        manager.process_events(event)
    manager.update(time_delta)

# Main loop setup
clock = pygame.time.Clock()

while True:
    if state == "menu":
        menu()
    elif state == "play":
        while state == "play":
            draw()
            event()
    pygame.display.flip()