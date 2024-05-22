import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
g = 9.81  # m/s^2, acceleration due to gravity
target_x = 2.00  # meters
target_y = 1.2  # meters
wall_x = 1.00  # meters
wall_y = 0.60  # meters
h = 0.3226  # initial height (meters)

# User-specified angle
theta_user = 45  # degrees

# Function to calculate the position of the projectile
def projectile_motion(v0, theta, t):
    theta_rad = np.radians(theta)
    x = v0 * np.cos(theta_rad) * t
    y = h + v0 * np.sin(theta_rad) * t - 0.5 * g * t**2
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
        _, y = projectile_motion(v0[0], theta, target_x / (v0[0] * np.cos(np.radians(theta))))
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

# Time array for the trajectory
theta_rad = np.radians(theta_user)
t_max = 2 * v0_optimized * np.sin(theta_rad) / g
t_values = np.linspace(0, t_max, num=100)

# Animation function
def update(frame):
    x, y = projectile_motion(v0_optimized, theta_user, t_values[frame])
    projectile.set_data(x, y)
    return projectile,

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot([wall_x, wall_x], [0, wall_y], color='black', label='Wall')
ax.scatter(target_x, target_y, color='red', label='Target')
ax.set_title(f'Optimized $v_0$={v0_optimized:.4f} m/s')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Height (m)')
ax.legend()
ax.grid(True)
ax.set_xlim(0, max(target_x, wall_x) + 1)
ax.set_ylim(0, max(target_y, wall_y) + 1)

# Create the projectile point
projectile, = ax.plot([], [], 'bo')

# Create the animation
ani = FuncAnimation(fig, update, frames=len(t_values), blit=True, interval=2)

# Show the animation
plt.show()
