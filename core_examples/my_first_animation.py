from SwarmSwIM import Simulator
from SwarmSwIM import Plotter
import matplotlib.pyplot as plt

# import os
# DIR_FILE = os.path.dirname(__file__)

# initiate simulator at 24 fps
S = Simulator(1/24, sim_xml="my_sim.xml")
# S = Simulator(1/24, sim_xml=os.path.join(DIR_FILE,"my_sim.xml"))

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

# Test acoustic ranging
# range = S.acoustic_range(S.agents[0], S.agents[1])
# range_OWTT = S.OWTT_acoustic_range(S.agents[0], S.agents[1])
# doppler = S.doppler(S.agents[0], S.agents[1])
# print (f"acustion range {range:.2f} m \
#        \nwith clock drift {range_OWTT:.2f} m \
#        \nDoppler {doppler:.3f} m/s")