from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
import matplotlib.pyplot as plt


# initiate simulator at 24 fps
S = Simulator(1/24, sim_xml="my_sim.xml")

for agent in S.agents:
    agent.cmd_fhd(forceNewton=2.5, headingDegrees=180, depthMeters=0.5)

# adding optinal graphics
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)
# initiate animator class
Animation = Plotter(S,artistics=[circle])

def animation_callback():
    """Move the simulation foward 1 step."""
    S.tick()  # advance 1 time step

# MAIN
Animation.update_plot(callback=animation_callback)