import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Constants
g = 9.81  # m/s^2, acceleration due to gravity
target_x = 2.00  # meters
target_y = 1.24  # meters
wall_x = 1.00  # meters
wall_y = 0.60  # meters
h = 0.3226  # initial height (meters)

# User-specified angle
theta_user = 45  # degrees

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
v0_optimized = optimize_v0(theta_user)

# Generate trajectory
def trajectory(v0, theta, num_points=1000):
    theta_rad = np.radians(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / g
    t = np.linspace(0, t_max, num_points)
    x = v0 * np.cos(theta_rad) * t
    y = h + v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    return x, y

x_trajectory, y_trajectory = trajectory(v0_optimized, theta_user)
print(v0_optimized)

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(x_trajectory, y_trajectory, label='Projectile Trajectory')
plt.scatter(target_x, target_y, color='red', label='Target')
plt.plot([wall_x, wall_x], [0, wall_y], color='black', label='Wall')
plt.title(f'Optimized $v_0$={v0_optimized:.4f} m/s')
plt.xlabel('Distance (m)')
plt.ylabel('Height (m)')
plt.legend()
plt.grid(True)
plt.show()
