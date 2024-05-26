import pygame
import pygame_gui
import numpy as np
import sys
from scipy.optimize import minimize
import math


# Class to manage the properties and methods related to the equilateral triangle
class Triangle:
    def __init__(self, width, height, side_length):
        # Initialize triangle parameters and vertices
        self._width = width  # Width of the screen
        self._height = height  # Height of the screen
        self._side_length = side_length  # Side length of the equilateral triangle

        # Calculate the height of the equilateral triangle
        self._triangle_height = (math.sqrt(3) / 2) * self._side_length

        # Calculate horizontal and vertical margins to center the triangle on the screen
        self._horizontal_margin = (self._width - self._side_length) / 2
        self._vertical_margin = (self._height - self._triangle_height) / 2

        # Define the vertices of the triangle
        self._vertex1 = (self._width // 2, int(self._vertical_margin))
        self._vertex2 = (
            int(self._horizontal_margin),
            int(self._height - self._vertical_margin),
        )
        self._vertex3 = (
            int(self._width - self._horizontal_margin),
            int(self._height - self._vertical_margin),
        )

    # Helper function to calculate the sign of an area
    def sign(self, p1, p2, p3):
        # This function helps determine the relative position of a point with respect to the triangle's edges
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    # Function to check if a point is inside the triangle
    def point_in_triangle(self, pz, py, v1, v2, v3):
        # Check if the point (pz, py) lies within the triangle defined by vertices v1, v2, and v3
        b1 = self.sign((pz, py), v1, v2) < 0.0
        b2 = self.sign((pz, py), v2, v3) < 0.0
        b3 = self.sign((pz, py), v3, v1) < 0.0
        return (b1 == b2) and (b2 == b3)

    # Function to check if a circle is entirely inside the triangle
    def circle_in_triangle(self, cz, cy, rad, v1, v2, v3):
        # Check if all points on the circumference of the circle lie within the triangle
        for angle in range(0, 360, 1):
            pz = cz + rad * math.cos(math.radians(angle))
            py = cy + rad * math.sin(math.radians(angle))
            if not self.point_in_triangle(pz, py, v1, v2, v3):
                return False
        return True


# Class to handle physics and optimization calculations for the projectile
class Projectile:
    def __init__(self, g, h, target_x, wall_x, wall_y):
        # Initialize projectile parameters
        self._g = g  # Acceleration due to gravity
        self._h = h  # Initial height of the projectile
        self._target_x = target_x  # Horizontal distance to the target
        self._wall_x = wall_x  # Horizontal distance to the wall
        self._wall_y = wall_y  # Height of the wall

    # Calculate the projectile motion to a target x position
    def projectile_motion(self, v0, theta):
        # Calculate the time to reach the target x position
        theta_rad = np.radians(theta)
        time_to_target_x = self._target_x / (v0 * np.cos(theta_rad))

        # Calculate the x and y positions at the target x position
        x = v0 * np.cos(theta_rad) * time_to_target_x
        y = (
            self._h
            + v0 * np.sin(theta_rad) * time_to_target_x
            - 0.5 * self._g * time_to_target_x**2
        )
        return x, y

    # Calculate the y position of the projectile at a specific wall x position
    def y_at_wall(self, v0, theta):
        # Calculate the time to reach the wall x position
        theta_rad = np.radians(theta)
        time_to_wall_x = self._wall_x / (v0 * np.cos(theta_rad))

        # Calculate the y position at the wall x position
        y_wall = (
            self._h
            + v0 * np.sin(theta_rad) * time_to_wall_x
            - 0.5 * self._g * time_to_wall_x**2
        )
        return y_wall

    # Optimize the initial velocity (v0) to hit the target y position
    def optimize_v0(self, theta, target_y):
        # Objective function to minimize the difference between actual and target y positions
        def objective(v0):
            _, y = self.projectile_motion(v0[0], theta)
            return abs(target_y - y)

        # Constraint to ensure the projectile clears the wall
        def constraint(v0):
            return self.y_at_wall(v0[0], theta) - self._wall_y

        # Initial guess, bounds, and constraints for the optimization
        initial_guess = [10]
        bounds = [(1, 100)]
        cons = [{"type": "ineq", "fun": constraint}]

        # Perform the optimization to find the optimal initial velocity
        result = minimize(
            objective, initial_guess, method="SLSQP", bounds=bounds, constraints=cons
        )
        return result.x[0]

    # Generate the trajectory points for the projectile motion
    def trajectory(self, v0, theta, num_points=1000):
        # Calculate the time intervals and positions for the projectile's trajectory
        theta_rad = np.radians(theta)
        t_max = 2 * v0 * np.sin(theta_rad) / self._g
        t = np.linspace(0, t_max, num_points)
        x = v0 * np.cos(theta_rad) * t
        y = self._h + v0 * np.sin(theta_rad) * t - 0.5 * self._g * t**2
        return x, y
    
    # Find voltage require for v0
    def voltage_require(self, v0):
        voltage_optimized = v0
        return voltage_optimized


# Class to manage the GUI elements and drawing
class SimulatorGUI:
    def __init__(self, screen, manager, width, height, colors, font):
        self._screen = screen  # Pygame screen
        self._manager = manager  # Pygame GUI manager
        self._width = width  # Screen width
        self._height = height  # Screen height
        self._colors = colors  # Color dictionary
        self._font = font  # Font for text rendering
        self._animating = False  # Animation state
        self._point_index = 0  # Index for animating points

        # Define rectangles for UI buttons
        self._back_button_rect = pygame.Rect(50, 790, 200, 50)
        self._start_stop_button_rect = pygame.Rect(1300, 735, 200, 50)
        self._reset_button_rect = pygame.Rect(1300, 795, 200, 50)

        # Load and scale the side view image
        self._side_view = pygame.image.load(
            "data/images/side_view_2024-05-21_151130-removebg-preview.png"
        )
        self._side_view = pygame.transform.scale(
            self._side_view, ((0.27 * 460 * 536) / 466, 0.27 * 460)
        )

    # Draw the setup screen
    def draw_setup(
        self,
        triangle,
        circle_z,
        circle_y,
        circle_radius,
        y_text_entry,
        z_text_entry,
        target_y,
        target_z,
    ):
        # Draw the setup UI components
        button_rect = pygame.Rect(50, 790, 200, 50)
        text_start = self._font.render("Calculate", True, self._colors["BLACK"])
        text_start_rect = text_start.get_rect(center=button_rect.center)

        # Fill the screen with the background color
        self._screen.fill(self._colors["GREY"])

        # Draw the equilateral triangle
        pygame.draw.polygon(
            self._screen,
            self._colors["WHITE"],
            [triangle._vertex1, triangle._vertex2, triangle._vertex3],
        )

        # Draw the circle inside the triangle
        pygame.draw.circle(
            self._screen, self._colors["GREY"], (circle_z, circle_y), circle_radius
        )

        # Draw a rectangle for the text entry area
        pygame.draw.rect(
            self._screen,
            self._colors["LIGHT_GREY"],
            pygame.Rect(570, 690, 460, 120),
            0,
            10,
        )

        # Draw the GUI manager
        self._manager.draw_ui(self._screen)

        # Change button color on hover
        mouse_pos = pygame.mouse.get_pos()
        calculate_color = (
            self._colors["DARKER_BLUE"]
            if button_rect.collidepoint(mouse_pos)
            else self._colors["BLUE"]
        )
        pygame.draw.rect(self._screen, calculate_color, button_rect, 0, 10)
        self._screen.blit(text_start, text_start_rect)

        # Draw the labels for target y and z text entries
        text = self._font.render("Target Y", True, self._colors["WHITE"])
        self._screen.blit(text, (620, 715))
        text = self._font.render("mm", True, self._colors["WHITE"])
        self._screen.blit(text, (880, 715))
        text = self._font.render("Target Z", True, self._colors["WHITE"])
        self._screen.blit(text, (620, 765))
        text = self._font.render("mm", True, self._colors["WHITE"])
        self._screen.blit(text, (880, 765))

        # Update the display
        pygame.display.flip()

    # Draw the simulation screen with projectile motion and UI elements
    def draw_simulation(
        self,
        origin_x,
        origin_y,
        target_x,
        target_y,
        target_z,
        wall_x,
        wall_y,
        v0_optimized,
        voltage_optimized,
        x_trajectory,
        y_trajectory,
    ):
        # Draw the simulation UI components
        self._screen.fill(self._colors["GREY"])
        pygame.draw.rect(
            self._screen,
            self._colors["LIGHT_GREY"],
            pygame.Rect(290, 715, 970, 150),
            0,
            10,
        )
        pygame.draw.rect(
            self._screen,
            self._colors["LIGHT_GREY"],
            pygame.Rect(1280, 715, 240, 150),
            0,
            10,
        )

        # Draw the back button
        back_text = self._font.render("Go back", True, self._colors["BLACK"])
        back_text_rect = back_text.get_rect(center=self._back_button_rect.center)
        start_stop_text = self._font.render("Start/Stop", True, self._colors["BLACK"])
        start_stop_text_rect = start_stop_text.get_rect(
            center=self._start_stop_button_rect.center
        )
        reset_text = self._font.render("Reset", True, self._colors["BLACK"])
        reset_text_rect = reset_text.get_rect(center=self._reset_button_rect.center)

        # Change button color on hover
        mouse_pos = pygame.mouse.get_pos()
        back_color = (
            self._colors["DARKER_BLUE"]
            if self._back_button_rect.collidepoint(mouse_pos)
            else self._colors["BLUE"]
        )
        pygame.draw.rect(self._screen, back_color, self._back_button_rect, 0, 10)
        self._screen.blit(back_text, back_text_rect)
        start_stop_color = (
            self._colors["DARKER_GREEN"]
            if self._start_stop_button_rect.collidepoint(mouse_pos)
            else self._colors["GREEN"]
        )
        pygame.draw.rect(
            self._screen, start_stop_color, self._start_stop_button_rect, 0, 10
        )
        self._screen.blit(start_stop_text, start_stop_text_rect)
        reset_color = (
            self._colors["DARKER_RED"]
            if self._reset_button_rect.collidepoint(mouse_pos)
            else self._colors["RED"]
        )
        pygame.draw.rect(self._screen, reset_color, self._reset_button_rect, 0, 10)
        self._screen.blit(reset_text, reset_text_rect)

        # Draw target position
        scale = 460  # Scale for converting meters to pixels
        target_pos = (origin_x + scale * target_x, origin_y - scale * target_y)
        pygame.draw.line(
            self._screen,
            self._colors["WHITE"],
            (target_pos[0], origin_y),
            (target_pos[0], origin_y - scale * 0.755),
            10,
        )
        pygame.draw.line(
            self._screen,
            self._colors["BLUE"],
            (target_pos[0], origin_y - (scale * 0.755)),
            (target_pos[0], origin_y - (scale * 0.755) - (scale * 0.03)),
            10,
        )
        pygame.draw.line(
            self._screen,
            self._colors["RED"],
            (target_pos[0], target_pos[1] + scale * 0.07),
            (target_pos[0], target_pos[1] - scale * 0.07),
            10,
        )

        # Draw wall position
        wall_pos_x = origin_x + scale * wall_x
        wall_top_y = origin_y - scale * wall_y
        pygame.draw.line(
            self._screen,
            self._colors["WHITE"],
            (wall_pos_x, origin_y),
            (wall_pos_x, wall_top_y),
            10,
        )

        # Draw scale lines
        for y in range(origin_y, int(origin_y - (scale * 1.4)) + 1, -23):
            pygame.draw.line(
                self._screen,
                self._colors["WHITE"],
                (origin_x - 150, y),
                (origin_x - 160, y),
                1,
            )
        pygame.draw.line(
            self._screen,
            self._colors["WHITE"],
            (origin_x - 160, origin_y + 5),
            (target_pos[0] + 5, origin_y + 5),
            10,
        )
        for x in range(origin_x, int(target_pos[0]) + 1, 23):
            pygame.draw.line(
                self._screen,
                self._colors["WHITE"],
                (x, origin_y + 10),
                (x, origin_y + 20),
                1,
            )

        # Draw the side view image
        self._screen.blit(
            self._side_view,
            (origin_x - (0.27 * scale * 536) / 466, origin_y - 0.27 * scale),
        )

        # Display the optimized initial velocity and target z position and voltage requirement
        text_optimized_v0 = self._font.render(
            f"Optimized v0: {v0_optimized:.4f} m/s", True, self._colors["WHITE"]
        )
        self._screen.blit(text_optimized_v0, (320, 800))
        text_pos_z = self._font.render(
            f"Z position from the left side: {target_z} cm", True, self._colors["WHITE"]
        )
        self._screen.blit(text_pos_z, (320, 750))
        text_optimized_voltage = self._font.render(
            f"Optimized voltage: {voltage_optimized:.2f} V", True, self._colors["WHITE"]
        )
        self._screen.blit(text_optimized_voltage, (800, 800))

        # Draw the trajectory of the projectile
        points = [
            (origin_x + scale * x, origin_y - scale * y)
            for x, y in zip(x_trajectory, y_trajectory)
            if y >= 0
        ]
        if points:
            pygame.draw.lines(self._screen, self._colors["WHITE"], False, points, 2)

        # Animate the projectile along the trajectory
        if self._animating:
            if self._point_index < len(points):
                ball_pos = points[self._point_index]
                pygame.draw.circle(
                    self._screen, self._colors["RED"], ball_pos, 0.02 * scale
                )
                self._point_index += 15
            else:
                self._point_index = 0
        elif not self._animating and self._point_index > 0:
            ball_pos = points[self._point_index]
            pygame.draw.circle(
                self._screen, self._colors["RED"], ball_pos, 0.02 * scale
            )
        if self._point_index >= len(points):
            self._point_index = 0

        pygame.display.flip()

    # Handle events such as button clicks and updates
    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_button_rect.collidepoint(event.pos):
                return "setup"
            if self._start_stop_button_rect.collidepoint(event.pos):
                self._animating = not self._animating
            if self._reset_button_rect.collidepoint(event.pos):
                self._animating = False
                self._point_index = 0
        return None

    # Reset the animation
    def reset(self):
        self._animating = False
        self._point_index = 0


# Main class to initialize everything and run the main loop
class ProjectileSimulator:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Projectile Simulator")
        self._state = "setup"  # Initial state of the simulator

        # Screen dimensions and setup
        self._width, self._height = 1600, 900
        self._screen = pygame.display.set_mode((self._width, self._height))

        # Color definitions
        self._colors = {
            "BLACK": (0, 0, 0),
            "WHITE": (217, 217, 217),
            "RED": (209, 106, 106),
            "DARKER_RED": (159, 56, 56),
            "GREEN": (178, 251, 165),
            "DARKER_GREEN": (128, 201, 115),
            "BLUE": (172, 230, 255),
            "DARKER_BLUE": (122, 180, 205),
            "GREY": (30, 30, 30),
            "LIGHT_GREY": (50, 50, 50),
        }

        self._font = pygame.font.Font(None, 36)  # Font for text rendering

        # Create triangle and projectile objects
        self._triangle = Triangle(self._width, self._height, 500)
        self._circle_radius = 69
        self._circle_z = self._triangle._vertex1[0]
        self._circle_y = self._height - (
            self._triangle._vertex1[1] + self._circle_radius
        )

        # Projectile physics parameters
        self._g = 9.81  # Gravity
        self._h = 0.3  # Initial height of the projectile
        self._target_x = 2.00  # Target x position
        self._wall_x = 1.00  # Wall x position
        self._wall_y = 0.60  # Wall height
        self._theta = 45  # Launch angle

        self._target_y = 0.755 + 0.007  # Target y position
        self._target_z = 250  # Target z position in cm

        self._projectile = Projectile(
            self._g, self._h, self._target_x, self._wall_x, self._wall_y
        )
        self._v0_optimized = self._projectile.optimize_v0(self._theta, self._target_y)
        self._voltage_optimized = self._projectile.voltage_require(self._v0_optimized)

        # Calculate the trajectory of the projectile
        self._x_trajectory, self._y_trajectory = self._projectile.trajectory(
            self._v0_optimized, self._theta
        )

        # Initialize GUI manager and text entry elements
        self._manager = pygame_gui.UIManager((self._width, self._height))
        self._y_text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((730, 700), (140, 50)), manager=self._manager
        )
        self._y_text_entry.set_text(str(70))
        self._z_text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((730, 750), (140, 50)), manager=self._manager
        )
        self._z_text_entry.set_text(str(250))

        self._gui = SimulatorGUI(
            self._screen,
            self._manager,
            self._width,
            self._height,
            self._colors,
            self._font,
        )

        self._clock = pygame.time.Clock()  # Clock for managing frame rate

    # Run the setup loop
    def run_setup(self):
        setup_running = True
        while setup_running and self._state == "setup":
            time_delta = self._clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    button_rect = pygame.Rect(50, 790, 200, 50)
                    if button_rect.collidepoint(event.pos):
                        self._state = "play"
                        setup_running = False

                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self._y_text_entry:
                        try:
                            temp_y = int(self._y_text_entry.get_text())
                            test_y = (
                                self._height - self._triangle._vertical_margin - temp_y
                            )
                            self._target_y = (temp_y / 1000) + 0.755
                            if self._triangle.circle_in_triangle(
                                self._circle_z,
                                test_y,
                                self._circle_radius,
                                self._triangle._vertex1,
                                self._triangle._vertex2,
                                self._triangle._vertex3,
                            ):
                                self._circle_y = test_y
                        except ValueError:
                            self._y_text_entry.set_text(
                                str(
                                    int(
                                        self._height
                                        - self._triangle._vertical_margin
                                        - self._circle_y
                                    )
                                )
                            )
                    elif event.ui_element == self._z_text_entry:
                        try:
                            temp_z = int(self._z_text_entry.get_text())
                            test_z = int(self._triangle._horizontal_margin) + temp_z
                            self._target_z = temp_z / 10
                            if self._triangle.circle_in_triangle(
                                test_z,
                                self._circle_y,
                                self._circle_radius,
                                self._triangle._vertex1,
                                self._triangle._vertex2,
                                self._triangle._vertex3,
                            ):
                                self._circle_z = test_z
                        except ValueError:
                            self._z_text_entry.set_text(
                                str(
                                    int(
                                        self._circle_z
                                        - self._triangle._horizontal_margin
                                    )
                                )
                            )

                self._manager.process_events(event)

            self._manager.update(time_delta)
            self._gui.draw_setup(
                self._triangle,
                self._circle_z,
                self._circle_y,
                self._circle_radius,
                self._y_text_entry,
                self._z_text_entry,
                self._target_y,
                self._target_z,
            )

    # Run the simulation loop
    def run_simulation(self):
        while self._state == "play":
            self._gui.draw_simulation(
                300,
                self._height - 230,
                self._target_x,
                self._target_y,
                self._target_z,
                self._wall_x,
                self._wall_y,
                self._v0_optimized,
                self._voltage_optimized,
                self._x_trajectory,
                self._y_trajectory,
            )
            for event in pygame.event.get():
                new_state = self._gui.handle_events(event)
                if new_state:
                    self._state = new_state
                self._v0_optimized = self._projectile.optimize_v0(
                    self._theta, self._target_y
                )
                self._voltage_optimized = self._projectile.voltage_require(
                    self._v0_optimized
                )
                self._manager.process_events(event)
            self._manager.update(self._clock.tick(60) / 1000.0)

    # Main loop to switch between setup and simulation
    def run(self):
        while True:
            if self._state == "setup":
                self.run_setup()
            elif self._state == "play":
                self.run_simulation()


if __name__ == "__main__":
    ProjectileSimulator().run()
