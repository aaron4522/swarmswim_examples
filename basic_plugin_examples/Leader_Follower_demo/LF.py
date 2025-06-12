# Example of use of the CNNDetection Plugin for multiagent coordination

from SwarmSwIM import Simulator, Plotter, CNNDetection
import matplotlib.pyplot as plt

# Create a visual reference for the plot: A Circle of radius 20 meters
circle = plt.Circle((0, 0), 20, color='g', fill=False, alpha=0.5)

# Initiate the simulation, with time tsep if 0.05s and using the simulation description in the LF_sim file
S = Simulator(1/20,sim_xml='LF_sim.xml') 
# Initiate simulated detection plugin
Detection = CNNDetection()
# Add basic animation plugin
Animation = Plotter(S,artistics=[circle])

# Initial conditions: give the front agent fixed foward force command, with constant heading and depth
S.agents[-1].cmd_fhd(1.0, 0.0, 66)
# Emulate a bias error, different for each agent in a range of +/- 2 degrees
for agent in S.agents: agent.e_heading[0]=S.rnd.uniform(-2.0,2.0)

timer = 30
def animation_callback():
    ''' callback function, move the simulation foward 1 step'''
    global timer

    S.tick()                    # Advance dynamics of 1 time step
    Detection(S)                # Compute Detections

    # execture controller of follower agents
    execute_control(S.agents[0])    
    execute_control(S.agents[1])
    # every 20 seconds rotate leader 90 degrees
    if S.time > timer:
        timer += 20 # seconds
        S.agents[-1].cmd_heading += 90 # degrees

def execute_control(agent):
    
    d0 = 1.0 # desired relative distance between agents 
    # If nothing is detected command the robot foward at a reduced thrust
    if (len(agent.NNDetector)<=1): agent.cmd_fhd(0.5, 0.0, 66)
    # Else if at least one detection was succesfull
    else:
        target = [1000, 0]  # distance and relative heading of target agent to follow
        for key in agent.NNDetector:
            if key=='time_lapsed': continue
            # update the target with distance and heading of the closest agent detected
            if agent.NNDetector[key][0]<target[0]:
                target[0]=agent.NNDetector[key][0]
                target[1]=agent.NNDetector[key][1]

        # Apply a control based on the target relative position.
        agent.cmd_heading = (agent.measured_heading + target[1])%360  # point towards the target (pure pursuit)
        distance_error = target[0] - d0             
        agent.cmd_forces = [distance_error*0.6,0]        # simple proportional distance control

# MAIN
Animation.update_plot(callback=animation_callback)
