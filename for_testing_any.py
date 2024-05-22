import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 9.8
SCALE = 20  # Scale to adjust the motion to the screen size
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Projectile Motion Simulation")
clock = pygame.time.Clock()

# Ball properties
ball_radius = 10
ball_color = RED

# Initial conditions
initial_velocity = 5  # Initial velocity in m/s
angle = 45  # Launch angle in degrees
angle_rad = math.radians(angle)
initial_x = 50
initial_y = SCREEN_HEIGHT - 50
ball_x = initial_x
ball_y = initial_y
velocity_x = initial_velocity * math.cos(angle_rad)
velocity_y = -initial_velocity * math.sin(angle_rad)
time = 0
running = False

# Buttons
font = pygame.font.Font(None, 36)
start_stop_button = pygame.Rect(50, 50, 100, 50)
reset_button = pygame.Rect(200, 50, 100, 50)

def reset():
    global ball_x, ball_y, velocity_x, velocity_y, time, running
    ball_x = initial_x
    ball_y = initial_y
    velocity_x = initial_velocity * math.cos(angle_rad)
    velocity_y = -initial_velocity * math.sin(angle_rad)
    time = 0
    running = False

# Main loop
running_simulation = True
while running_simulation:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_simulation = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_stop_button.collidepoint(event.pos):
                running = not running
            elif reset_button.collidepoint(event.pos):
                reset()

    if running:
        time += 1 / FPS
        ball_x = initial_x + velocity_x * time * SCALE
        ball_y = initial_y + (velocity_y * time + 0.5 * GRAVITY * time ** 2) * SCALE

    # Check if the ball hits the ground
    if ball_y > SCREEN_HEIGHT - ball_radius:
        running = False

    # Drawing
    screen.fill(WHITE)
    pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)

    pygame.draw.rect(screen, BLACK, start_stop_button)
    pygame.draw.rect(screen, BLACK, reset_button)
    start_stop_text = font.render("Start/Stop", True, WHITE)
    reset_text = font.render("Reset", True, WHITE)
    screen.blit(start_stop_text, (start_stop_button.x + 10, start_stop_button.y + 10))
    screen.blit(reset_text, (reset_button.x + 10, reset_button.y + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
