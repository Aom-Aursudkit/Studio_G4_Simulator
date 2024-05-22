import pygame
import pygame_gui
import numpy as np
import sys
from scipy.optimize import minimize
import math

class ProjectileSimulator:
    def __init__(self):
        # Initialize Pygame and pygame_gui
        pygame.init()
        pygame.display.set_caption("Projectile Simulator")
        self._state = "menu"
        
        # Screen dimensions and colors
        self._width, self._height = 1600, 900
        self._screen = pygame.display.set_mode((self._width, self._height))
        
        # Colors
        self._BLACK = (0, 0, 0)
        self._WHITE = (217, 217, 217)
        self._RED = (209, 106, 106)
        self._GREEN = (0, 255, 102)
        self._DARKER_GREEN = (0, 200, 0)
        self._LIGHT_BLUE = (172, 230, 255)
        self._BLUE = (122, 180, 205)
        self._background_color = (30, 30, 30)  # Dark gray
        
        self._font = pygame.font.Font(None, 36)
        
        # Equilateral triangle specifications
        self._side_length = 500
        self._triangle_height = (math.sqrt(3) / 2) * self._side_length
        self._horizontal_margin = (self._width - self._side_length) / 2
        self._vertical_margin = (self._height - self._triangle_height) / 2
        
        # Triangle vertices
        self._vertex1 = (self._width // 2, int(self._vertical_margin))
        self._vertex2 = (int(self._horizontal_margin), int(self._height - self._vertical_margin))
        self._vertex3 = (int(self._width - self._horizontal_margin), int(self._height - self._vertical_margin))
        
        # Circle
        self._circle_radius = 69
        self._circle_z, self._circle_y = self._vertex1[0], self._height - (self._vertex1[1] + self._circle_radius)
        
        # Animating
        self._point_index = 0
        self._animating = False
        self._time_elapsed = 0
        
        # Image
        self._side_view = pygame.image.load("data/images/side_view_2024-05-21_151130-removebg-preview.png")
        self._side_view = pygame.transform.scale(self._side_view, ((0.27 * 460 * 536) / 466, 0.27 * 460))
        
        # GUI Manager for pygame_gui
        self._manager = pygame_gui.UIManager((self._width, self._height))
        
        # GUI Elements ###################################################
        # Text box for y-coordinate
        self._y_text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((730, 700), (150, 50)), manager=self._manager)
        self._y_text_entry.set_text(str(70))
        
        # Text box for z-coordinate
        self._z_text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((730, 750), (150, 50)), manager=self._manager)
        self._z_text_entry.set_text(str(250))
        ##################################################################
        
        # Constants
        self._g = 9.81  # m/s^2, acceleration due to gravity
        self._target_x = 2.00  # meters
        self._wall_x = 1.00  # meters
        self._wall_y = 0.60  # meters
        self._theta = 45  # angle in degrees
        self._h = 0.3
        self._target_z = 250
        self._target_y = 0.755 + 0.007
        
        self._temp_y = 70
        self._test_y = self._height - self._vertical_margin - self._temp_y
        self._circle_y = self._test_y
        self._target_y = (self._temp_y / 1000) + 0.755
        
        self._temp_z = 250
        self._test_z = int(self._horizontal_margin) + self._temp_z
        self._circle_z = self._test_z
        self._target_z = self._temp_z / 10
        
        # Projectile
        self._v0_optimized = self.optimize_v0(self._theta)
        
        # Trajectory
        self._x_trajectory, self._y_trajectory = self.trajectory(self._v0_optimized, self._theta)
        
        # State
        self._clock = pygame.time.Clock()
    
    def sign(self, p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    def point_in_triangle(self, pz, py, v1, v2, v3):
        b1 = self.sign((pz, py), v1, v2) < 0.0
        b2 = self.sign((pz, py), v2, v3) < 0.0
        b3 = self.sign((pz, py), v3, v1) < 0.0
        return (b1 == b2) and (b2 == b3)
    
    def circle_in_triangle(self, cz, cy, rad, v1, v2, v3):
        for angle in range(0, 360, 1):  # Check every 1 degree
            pz = cz + rad * math.cos(math.radians(angle))
            py = cy + rad * math.sin(math.radians(angle))
            if not self.point_in_triangle(pz, py, v1, v2, v3):
                return False
        return True
    
    def projectile_motion(self, v0, theta):
        theta_rad = np.radians(theta)
        # Time when projectile is at self._target_x
        time_to_target_x = self._target_x / (v0 * np.cos(theta_rad))
        # Position calculation
        x = v0 * np.cos(theta_rad) * time_to_target_x
        y = self._h + v0 * np.sin(theta_rad) * time_to_target_x - 0.5 * self._g * time_to_target_x**2
        return x, y
    
    def y_at_wall(self, v0, theta):
        theta_rad = np.radians(theta)
        time_to_wall_x = self._wall_x / (v0 * np.cos(theta_rad))
        y_wall = self._h + v0 * np.sin(theta_rad) * time_to_wall_x - 0.5 * self._g * time_to_wall_x**2
        return y_wall
    
    def optimize_v0(self, theta):
        def objective(v0):
            _, y = self.projectile_motion(v0[0], theta)
            return abs(self._target_y - y)
        
        def constraint(v0):
            return self.y_at_wall(v0[0], theta) - self._wall_y
        
        initial_guess = [10]
        bounds = [(1, 100)]
        cons = [{"type": "ineq", "fun": constraint}]
        
        result = minimize(objective, initial_guess, method="SLSQP", bounds=bounds, constraints=cons)
        return result.x[0]
    
    def trajectory(self, v0, theta, num_points=1000):
        theta_rad = np.radians(theta)
        t_max = 2 * v0 * np.sin(theta_rad) / self._g
        t = np.linspace(0, t_max, num_points)
        x = v0 * np.cos(theta_rad) * t
        y = self._h + v0 * np.sin(theta_rad) * t - 0.5 * self._g * t**2
        return x, y
    
    def trajec_animating(self, v0, theta, num_points=1000):
        theta_rad = np.radians(theta)
        t_max = 2 * v0 * np.sin(theta_rad) / self._g
        t_intervals = [t_max * i / num_points for i in range(num_points + 1)]
        t = np.linspace(0, t_max, num_points)
        x = v0 * np.cos(theta_rad) * t
        y = self._h + v0 * np.sin(theta_rad) * t - 0.5 * self._g * t**2
        return x, y, t_intervals
    
    def menu(self):
        button_rect = pygame.Rect(50, 50, 200, 50)
        text_start = self._font.render("Calculate", True, self._BLACK)
        text_start_rect = text_start.get_rect(center=button_rect.center)
        self._animating = False
        self._point_index = 0
        self._time_elapsed = 0
        
        menu_running = True
        while menu_running and self._state == "menu":
            time_delta = self._clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        self._state = "play"
                        menu_running = False
                
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self._y_text_entry:
                        try:
                            temp_y = int(self._y_text_entry.get_text())
                            test_y = self._height - self._vertical_margin - temp_y
                            self._target_y = (temp_y / 1000) + 0.755
                            if self.circle_in_triangle(self._circle_z, test_y, self._circle_radius, self._vertex1, self._vertex2, self._vertex3):
                                self._circle_y = test_y
                        except ValueError:
                            self._y_text_entry.set_text(str(int(self._height - self._vertical_margin - self._circle_y)))
                    elif event.ui_element == self._z_text_entry:
                        try:
                            temp_z = int(self._z_text_entry.get_text())
                            test_z = int(self._horizontal_margin) + temp_z
                            self._target_z = temp_z / 10
                            if self.circle_in_triangle(test_z, self._circle_y, self._circle_radius, self._vertex1, self._vertex2, self._vertex3):
                                self._circle_z = test_z
                        except ValueError:
                            self._z_text_entry.set_text(str(int(self._circle_z - self._horizontal_margin)))
                
                self._manager.process_events(event)
            
            self._manager.update(time_delta)
            
            # Fill the screen with a nicer background color
            self._screen.fill(self._background_color)
            
            # Draw the triangle with a nicer color
            pygame.draw.polygon(self._screen, self._WHITE, [self._vertex1, self._vertex2, self._vertex3])
            
            # Draw the circle
            pygame.draw.circle(self._screen, self._background_color, (self._circle_z, self._circle_y), self._circle_radius)
            
            self._manager.draw_ui(self._screen)
            
            mouse_pos = pygame.mouse.get_pos()
            current_color = self._BLUE if button_rect.collidepoint(mouse_pos) else self._LIGHT_BLUE
            pygame.draw.rect(self._screen, current_color, button_rect)
            self._screen.blit(text_start, text_start_rect)
            
            text = self._font.render("Target Y", True, self._WHITE)
            self._screen.blit(text, (620, 715))
            text = self._font.render("mm", True, self._WHITE)
            self._screen.blit(text, (890, 715))
            text = self._font.render("Target Z", True, self._WHITE)
            self._screen.blit(text, (620, 765))
            text = self._font.render("mm", True, self._WHITE)
            self._screen.blit(text, (890, 765))
            
            # Update the display
            pygame.display.flip()
    
    def draw(self):
        self._screen.fill(self._background_color)
        
        # Button
        self._back_button_rect = pygame.Rect(50, 50, 200, 50)
        back_text = self._font.render("Go back", True, self._BLACK)
        back_text_rect = back_text.get_rect(center=self._back_button_rect.center)
        
        self._start_stop_button_rect = pygame.Rect(50, 110, 200, 50)
        start_stop_text = self._font.render("Start/Stop", True, self._BLACK)
        start_stop_text_rect = start_stop_text.get_rect(center=self._start_stop_button_rect.center)
        
        self._reset_button_rect = pygame.Rect(260, 110, 200, 50)
        reset_text = self._font.render("Reset", True, self._BLACK)
        reset_text_rect = reset_text.get_rect(center=self._reset_button_rect.center)
        
        mouse_pos = pygame.mouse.get_pos()
        back_color = self._BLUE if self._back_button_rect.collidepoint(mouse_pos) else self._LIGHT_BLUE
        pygame.draw.rect(self._screen, back_color, self._back_button_rect)
        self._screen.blit(back_text, back_text_rect)
        
        start_stop_color = self._BLUE if self._start_stop_button_rect.collidepoint(mouse_pos) else self._LIGHT_BLUE
        pygame.draw.rect(self._screen, start_stop_color, self._start_stop_button_rect)
        self._screen.blit(start_stop_text, start_stop_text_rect)
        
        reset_color = self._BLUE if self._reset_button_rect.collidepoint(mouse_pos) else self._LIGHT_BLUE
        pygame.draw.rect(self._screen, reset_color, self._reset_button_rect)
        self._screen.blit(reset_text, reset_text_rect)
        
        # Vert coordinates to pixels
        scale = 460  # pixels per meter
        origin_x = 300
        origin_y = self._height - 70
        
        # Draw target
        target_pos = (origin_x + scale * self._target_x, origin_y - scale * self._target_y)
        pygame.draw.line(self._screen, self._WHITE, (target_pos[0], origin_y), (target_pos[0], origin_y - scale * 0.755), 10)
        pygame.draw.line(self._screen, self._BLUE, (target_pos[0], origin_y - (scale * 0.755)), (target_pos[0], origin_y - (scale * 0.755) - (scale * self._triangle_height / 1000)), 10)
        pygame.draw.line(self._screen, self._RED, (target_pos[0], target_pos[1] + scale * 0.07), (target_pos[0], target_pos[1] - scale * 0.07), 10)
        
        # Draw wall
        wall_pos_x = origin_x + scale * self._wall_x
        wall_top_y = origin_y - scale * self._wall_y
        pygame.draw.line(self._screen, self._WHITE, (wall_pos_x, origin_y), (wall_pos_x, wall_top_y), 10)
        
        # Draw scale
        for y in range(origin_y, int(origin_y - (scale * 1.4)) + 1, -23):
            pygame.draw.line(self._screen, self._WHITE, (origin_x - 150, y), (origin_x - 160, y), 1)
        pygame.draw.line(self._screen, self._WHITE, (origin_x - 160, origin_y + 5), (target_pos[0] + 5, origin_y + 5), 10)
        for x in range(origin_x, int(target_pos[0]) + 1, 23):
            pygame.draw.line(self._screen, self._WHITE, (x, origin_y + 10), (x, origin_y + 20), 1)
        
        # Import image
        self._screen.blit(self._side_view, (origin_x - (0.27 * scale * 536) / 466, origin_y - 0.27 * scale))
        
        # Display output
        text = self._font.render(f"Optimized v0: {self._v0_optimized:.4f} m/s", True, self._WHITE)
        self._screen.blit(text, (300, 50))
        text_pos_z = self._font.render(f"Z position from the left side: {self._target_z} cm", True, self._WHITE)
        self._screen.blit(text_pos_z, (750, 50))
        
        # Draw trajectory
        x_traj, y_traj = self.trajectory(self._v0_optimized, self._theta, num_points=100)
        points = [(origin_x + scale * x, origin_y - scale * y) for x, y in zip(x_traj, y_traj) if y >= 0]
        if points:
            pygame.draw.lines(self._screen, self._WHITE, False, points, 2)
        
        # Animating trajectory
        x_traj, y_traj, t_intervals = self.trajec_animating(self._v0_optimized, self._theta, num_points=100)
        points = [(origin_x + scale * x, origin_y - scale * y) for x, y in zip(x_traj, y_traj) if y >= 0]
        if self._animating and self._point_index < len(points):
            self._time_elapsed += self._clock.get_time() / 1000  # Time in seconds
            while self._point_index < len(points) - 1 and self._time_elapsed >= t_intervals[self._point_index]:
                self._point_index += 1
            if self._point_index < len(points):
                ball_pos = points[self._point_index]
                pygame.draw.circle(self._screen, self._RED, ball_pos, 0.02 * scale)
        elif not self._animating and self._point_index > 0:
            ball_pos = points[self._point_index]
            pygame.draw.circle(self._screen, self._RED, ball_pos, 0.02 * scale)
        
        pygame.display.flip()
    
    def event(self):
        time_delta = self._clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._back_button_rect.collidepoint(event.pos):
                    self._state = "menu"
                if self._start_stop_button_rect.collidepoint(event.pos):
                    self._animating = not self._animating
                if self._reset_button_rect.collidepoint(event.pos):
                    self._animating = False
                    self._point_index = 0
                    self._time_elapsed = 0
            self._v0_optimized = self.optimize_v0(self._theta)  # Update the velocity each time the input changes
            self._manager.process_events(event)
        self._manager.update(time_delta)
    
    def run(self):
        while True:
            if self._state == "menu":
                self.menu()
            elif self._state == "play":
                while self._state == "play":
                    self.draw()
                    self.event()
            pygame.display.flip()

if __name__ == "__main__":
    ProjectileSimulator().run()
