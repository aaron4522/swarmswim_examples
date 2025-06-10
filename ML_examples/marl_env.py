import numpy as np
import os

from SwarmSwIM import Simulator, CNNDetection

from ray.rllib.env import MultiAgentEnv
from gymnasium.spaces import Box

FOLDER = os.path.dirname(os.path.abspath(__file__)) 
file_sim = FOLDER+'/MARL_sim.xml'

MISSION_TIME = 200

RW_RANGE = 12.0 # radius [m]
RW_WIDTH = 0.5  # width of reward zone [m]
MIL_PUN  =  -1  # punihsment for distance from mil radius
MIL_REW  = 0.5  # reward at perfect radius

COL_DST  = 0.25 # collision happened distance
COL_PUN  = -100 # collision punishment
COL_RNG  =  1.0 # collision range dist [m] 

GOAL_DST =  2.0 # distance to front goal [m]
GOAL_RNG =  1.0 # width of reward zone [m]
GOAL_RW  =  0.5 # goal reward score

MAX_FRC   = 1.0
MAX_OMEGA = 60

prev_dists = [0]*6

class SimWrapperEnv(MultiAgentEnv):
    def __init__(self,config=None):
        super().__init__()
        self.timeSubdivision = 0.1
        # create new simulation
        self.sim = Simulator(self.timeSubdivision, sim_xml=file_sim)
        self.det = CNNDetection()
        self.agent_ids = [agent.name for agent in self.sim.agents]
        # required list of agents <- all always active
        self.agents = self.agent_ids
        self.possible_agents = self.agent_ids
        # define observer and action spaces
        self.observation_space = Box(low=0.0, high=21.0, shape=(3,),dtype=np.float32)
        self.observation_spaces = {agent_id: self.observation_space for agent_id in self.agent_ids}
        
        low  = np.array([MAX_FRC/20, -MAX_OMEGA], dtype=np.float32)
        high = np.array([   MAX_FRC,  MAX_OMEGA], dtype=np.float32)
        self.action_space = Box(low=low, high=high, dtype=np.float32)
        self.action_spaces = {agent_id: self.action_space for agent_id in self.agent_ids}

        print(self.agent_ids)

    def reset(self, *, seed=None, options=None):
        # reinitialize simulator
        self.sim = Simulator(self.timeSubdivision, sim_xml=file_sim)
        #scramble initial positions a bit
        self.randomize_initial_pos()
        self.det = CNNDetection()
        observations = self.agents_observation()
        return observations,{}

    def step(self, action_dict):
        # check for new visual detection
        new_det = self.det(self.sim)
        # apply control to all agents that have recived a new visual detection
        for key in action_dict:
            if not key in new_det: continue
            agent = next((agent for agent in self.sim.agents if agent.name == key), None)
            if agent == None: continue
            agent.cmd_forces  = action_dict[key][0]
            agent.cmd_yawrate = action_dict[key][1]
        # advance simulation
        self.sim.tick()
        # calculate rewards based on ground truth
        term    = self.done_terminated()
        obs = self.agents_observation()
        rewards = self.calculate_rewards(term['__all__'], obs)
        # check if time is out
        trunc = self.done_truncated()
        # print(f'obs: {self.agents_observation()}')
        # print(f'rew: {rewards}')
        # print(f'term: {term}')
        # print(f'trunc: {trunc}')
        return obs, rewards, term, trunc, {}
    
    def done_truncated(self):
        is_done = False if self.sim.time < MISSION_TIME else True
        result = {}
        result['__all__'] = is_done
        for agent_name in self.agent_ids:
            result[agent_name] = is_done
        return result
    
    def done_terminated(self):
        positions = np.array([agent.pos for agent in self.sim.agents])
        is_ok = False
        for i, agent in enumerate(self.sim.agents):
            rel_pos = positions - agent.pos
            rel_pos = np.delete(rel_pos, i, axis=0)
            distances = np.linalg.norm(rel_pos, axis=1)
            if min(distances) < COL_DST: 
                is_ok = True
                break
        
        result = {}
        result['__all__'] = is_ok
        for agent_name in self.agent_ids:
            result[agent_name] = is_ok
        return result

    def randomize_initial_pos(self):
        for agent in self.sim.agents:
            agent.pos[0]+= np.random.normal(3,0.75)
            agent.pos[1]+= np.random.normal(3,0.75)

    def agents_observation(self):
        observations = {}
        for agent in self.sim.agents:
            detections = agent.NNDetector
            threeranges = np.array([20.0,20.0,20.0], dtype=np.float32)
            for key in detections:
                if key=='time_lapsed': continue
                if -135 < agent.NNDetector[key][1] < -45 and threeranges[0]>agent.NNDetector[key][0]:
                    threeranges[0] = np.float32(agent.NNDetector[key][0])
                if -45 <= agent.NNDetector[key][1] <= 45 and threeranges[1]>agent.NNDetector[key][0]:
                    threeranges[1] = np.float32(agent.NNDetector[key][0])
                if  45 < agent.NNDetector[key][1] < 135  and threeranges[2]>agent.NNDetector[key][0]:
                    threeranges[2] = np.float32(agent.NNDetector[key][0])
            observations[agent.name] = threeranges
        return observations

    def calculate_rewards(self, term, obs):
        rewards_dict = {}
        positions = np.array([agent.pos for agent in self.sim.agents])
        for i, agent in enumerate(self.sim.agents):
            reward = 0
            rel_pos = positions - agent.pos
            rel_pos = np.delete(rel_pos, i, axis=0)
            angles = (np.arctan2(rel_pos[:, 1], rel_pos[:, 0])* 180 / np.pi - agent.psi) % 360
            angles[angles > 180] -= 360
            distances = np.linalg.norm(rel_pos, axis=1)
            closest = min(distances)
            
            # milling behavior (individual influence)
            mil_dist = np.linalg.norm(agent.pos[:2]) - RW_RANGE
            if abs(mil_dist) <= RW_WIDTH: reward += MIL_REW*abs(mil_dist)/RW_WIDTH
            else: reward += MIL_PUN*abs(mil_dist)

            # collision behavior
            if closest < COL_RNG: 
                reward += (1-(closest-COL_DST)/(COL_RNG-COL_DST))*COL_PUN

            # distance to front robot
            if obs:
                dist_to_front = obs[agent.name][1] - GOAL_DST
                if abs(dist_to_front) < GOAL_RNG: reward += GOAL_RW

            # terminatoon reward
            if term: rewards_dict[agent.name] = COL_PUN
            else:    rewards_dict[agent.name] = reward/100

        return rewards_dict


# SW = SimWrapperEnv()
# act = {'A01': 0.2, 'A02': -0.1}
# print(SW.reset()[0])

