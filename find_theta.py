import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Constants
g = 9.81  # m/s^2, acceleration due to gravity
target_x = 2.00  # meters
target_y = 1.125  # meters
wall_x = 1.00  # meters
wall_y = 0.60  # meters
h = 0.30  # initial height (meters)

# Given initial velocity for the optimization
v0_given = 5.778905145512891  # m/s

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

# Generate trajectory function
def trajectory(v0, theta, num_points=1000):
    theta_rad = np.radians(theta)
    t_max = 2 * v0 * np.sin(theta_rad) / g
    t = np.linspace(0, t_max, num_points)
    x = v0 * np.cos(theta_rad) * t
    y = h + v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
    return x, y

# Optimization function that adjusts theta for a given v0
def optimize_theta(v0):
    # Objective: Minimize the difference in y from the target at target_x
    def objective(theta):
        _, y = projectile_motion(v0, theta[0])
        return abs(target_y - y)
    
    # Constraint: Projectile must clear the wall
    def constraint(theta):
        return y_at_wall(v0, theta[0]) - wall_y
    
    # Initial guess for theta
    initial_guess = [45]  # degrees
    # Bounds for theta
    bounds = [(1, 89)]  # Avoiding exactly 90 degrees to prevent division by zero in calculations
    # Constraint
    cons = [{'type': 'ineq', 'fun': constraint}]
    
    # Run optimization
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=cons)
    return result.x[0]

# Find optimized theta for the given v0
theta_optimized_given_v0 = optimize_theta(v0_given)

# Generate trajectory with given v0 and optimized theta
x_trajectory_given_v0, y_trajectory_given_v0 = trajectory(v0_given, theta_optimized_given_v0)

# Output the optimized angle for the user's reference
print(theta_optimized_given_v0)

# Plotting for the scenario with given v0
plt.figure(figsize=(10, 5))
plt.plot(x_trajectory_given_v0, y_trajectory_given_v0, label=f'Projectile Trajectory at $v_0$={v0_given} m/s')
plt.scatter(target_x, target_y, color='red', label='Target')
plt.plot([wall_x, wall_x], [0, wall_y], color='black', linewidth=2, label='Wall')
plt.title(f'Projectile Motion for Optimized $\\theta$={theta_optimized_given_v0:.2f}° with $v_0$={v0_given} m/s')
plt.xlabel('Distance (m)')
plt.ylabel('Height (m)')
plt.legend()
plt.grid(True)
plt.show()
