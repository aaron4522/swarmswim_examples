# Provide an example of use of the AcousticChannel plugin, as a method for
# acoustic ranging. This example showcases a behavior based on such approach.

from SwarmSwIM import Simulator, Plotter, AcousticChannel
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# Create a visual reference for the plot: A Circle of radius 20 meters
circle = plt.Circle((0, 0), 10, color='g', fill=False, alpha=0.5)
# Initiate the simulation, with time tsep if 0.05s and using the simulation description in the LF_sim file
S = Simulator(1/20,sim_xml='RS_sim.xml') 
# Initiate simulated visual detection and acustic plugin
Acoustic = AcousticChannel()
# Add basic animation plugin
Animation = Plotter(S,artistics=[circle])
RANGE_LIMIT = 10.0 #meters

def opt_angle(angle_list,doppler_list):
    x1 = np.cos(np.deg2rad(angle_list))
    x2 = np.sin(np.deg2rad(angle_list))
    X = np.column_stack((x1, x2))
    regressor = LinearRegression(fit_intercept=False)
    regressor.fit(X, doppler_list)
    C1, C2 = regressor.coef_
    theta = (np.degrees(np.arctan2(C2, C1)))
    return (theta-180)%360

def cosine_model(x, A, f):
    return A * np.cos(np.radians(x) + f)

class AgentControl:
    def __init__(self, agent):
        self.agent = agent
        self.isinrange = True

        self.heading_history = [0.0]*10
        self.doppler_history = [0.0]*10
        
        self.random_update_period = 4.0
        self._next_random_time = S.time + self.random_update_period + S.rnd.uniform(high=4.0)
    
    def __call__(self):
        # Get and add latest doppler
        self.trigger_random(self.random_correction)

    def trigger_random (self, callback):
        if self._next_random_time<=S.time and self.isinrange:
            self._next_random_time += self.random_update_period
            callback()
    def random_correction(self):
        new_heading = (self.agent.cmd_heading + S.rnd.uniform(low=-30,high=30))%360
        # print(new_heading)
        self.agent.cmd_heading = new_heading

    def range_cmd(self, output):
        # update range if gets update
        if range_update_name and self.agent.name == range_update_name:
            range2beacon = S.acoustic_range(self.agent,S.agents[0])
            self.isinrange = True if range2beacon<=RANGE_LIMIT else False
        # if called answer
        if self.agent.name in output[0]:
            Acoustic.send(self.agent, S, duration=0.2, payload=f"Ping")
        # collect doppler 
        doppler_velocity = S.doppler(self.agent,S.agents[0])
        # history update
        self.doppler_history.append(doppler_velocity)
        self.doppler_history.pop(0)
        self.heading_history.append(self.agent.measured_heading)
        self.heading_history.pop(0)
        # if ouside the range try to return 
        if not self.isinrange:
            # calculate return direction on known info
            direction_back = opt_angle(self.heading_history,self.doppler_history)
            self.agent.cmd_heading = direction_back

controllers = []
beacon_update_period = 1.5
range_update_name = None
agent_call_index = 0

_next_beacon_time = S.time + beacon_update_period
def trigger_beacon (Dt, callback):
    global _next_beacon_time
    if _next_beacon_time<=S.time:
        _next_beacon_time += Dt
        callback()

def beacon_update():
    global agent_call_index
    Acoustic.send(S.agents[0], S, duration=0.6, payload=f"Beacon to {controllers[agent_call_index].agent.name}") 
    agent_call_index += 1
    if agent_call_index >= len(controllers): agent_call_index=0

def beacon_recive(Sender):
    global range_update_name
    for agent in S.agents:
        if not agent.name == Sender: continue
        range_update_name =  Sender


for agent in S.agents[1:]: 
    # Emulate a bias error, different for each agent in a range of +/- 2 degrees
    agent.e_heading[0]=S.rnd.uniform(-2.0,2.0)
    # create controller for each agent 
    controllers.append(AgentControl(agent))
    # constant force foward
    agent.cmd_forces = 2.0

# change first agent control to static in origin
S.agents[0].planar_control='ideal'



def animation_callback():
    global _next_trigger_time
    S.tick()                    # Advance dynamics of 1 time step
    
    recivers = Acoustic(S)       # process acoustic propagation
    
    if recivers: 
        if S.agents[0].name in recivers: 
            beacon_recive(recivers[S.agents[0].name][1])
        else:
            for key, output in recivers.items(): 
                for ctrl in controllers:
                    if key==ctrl.agent.name: 
                        ctrl.range_cmd(output)


    for control in controllers:
        control()

    trigger_beacon(beacon_update_period, beacon_update)


# MAIN
Animation.update_plot(callback=animation_callback)

