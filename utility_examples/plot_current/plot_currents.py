import matplotlib.pyplot as plt
import numpy as np

from SwarmSwIM import Simulator
from SwarmSwIM import Agent

S = Simulator(1/5, sim_xml='utility_sim.xml') 
S.agents = []

# Parameters
grid_size = 39  # 50x50 grid
spacing = 3  # 2 meters apart

# Create grid of x and y coordinates
x = np.arange(0, grid_size * spacing, spacing)
y = np.arange(0, grid_size * spacing, spacing)
x_grid, y_grid = np.meshgrid(x, y)

# Set z coordinates to 0
z_grid = np.zeros_like(x_grid)

# Combine into a list of np arrays
grid_points = [np.array([x, y, z]) for x, y, z in zip(x_grid.flatten(), y_grid.flatten(), z_grid.flatten())]

for i, point in enumerate (grid_points):
    S.add(Agent('A'+f'{i+1:04}',initialPosition=point))

S.tick()

new_points = []
for agent in S.agents:
    new_points.append(agent.pos)

x_orig = np.array([p[0] for p in grid_points])
y_orig = np.array([p[1] for p in grid_points])

x_new = np.array([p[0] for p in new_points])
y_new = np.array([p[1] for p in new_points])

# Calculate vector components (differences)
u = x_new - x_orig  # X component of vector
v = y_new - y_orig  # Y component of vector

# Plot the vector field
plt.figure(figsize=(8, 8))
plt.quiver(x_orig, y_orig, u, v, angles='xy', scale_units='xy', scale=0.08, color='r', label='Vector Field')
# plt.scatter(x_orig, y_orig, c='b', s=5, label='Grid Points')  # Original grid points
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Current Representation")
plt.axis("equal")
plt.grid(True)
plt.show()
