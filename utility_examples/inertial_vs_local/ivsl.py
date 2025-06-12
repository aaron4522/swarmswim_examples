from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
import matplotlib.pyplot as plt

import os
DIR_FILE = os.path.dirname(__file__)

# initiate simulator at 24 fps
S = Simulator(1/24, sim_xml=os.path.join(DIR_FILE,"ivsl_sim.xml"))
# change one agent to inertial
S.agents[0].planar_control = "inertial_velocity"

for agent in S.agents:
    agent.cmd_local_vel = [1.0]
    # agent.cmd_heading = 90

# adding optinal graphics
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)
# initiate animator class
Animation = Plotter(S,artistics=[circle])

def animation_callback():
    """Move the simulation foward 1 step."""
    S.tick()  # advance 1 time step

# MAIN
Animation.update_plot(callback=animation_callback)