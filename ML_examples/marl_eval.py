import matplotlib.pyplot as plt
import numpy as np
import os
from SwarmSwIM import Plotter, Simulator, CNNDetection

## GUI creation 
FOLDER = os.path.dirname(os.path.abspath(__file__)) 
file_sim = FOLDER+'/MARL_sim.xml'
# Create a visual reference for the plot: A Circle of radius 20 meters
circle = plt.Circle((0, 0), 12, color='g', fill=False, alpha=0.5)
sim_obj = Simulator(0.1, sim_xml=file_sim)
Animation = Plotter(sim_obj, artistics=[circle])
det_obj = CNNDetection()


import ray
from ray.rllib.algorithms.ppo import PPO
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
import gymnasium as gym

import torch
from torch.distributions import Normal

from marl_env import SimWrapperEnv


ray.init(ignore_reinit_error=True)
def env_creator(config):
    return SimWrapperEnv(config)
register_env("multi_agent_swarm_env", env_creator)

# --- swarswim_env env to extract spaces and agent ids ---
swarswim_env = SimWrapperEnv()
obs_space = swarswim_env.observation_space
act_space = swarswim_env.action_space
agent_ids = swarswim_env.agent_ids

# --- Shared policy ---
shared_policy_id = "shared_policy"
policies = { shared_policy_id: (None, obs_space, act_space, {}) }
def policy_mapping_fn(agent_id, *args, **kwargs):
    return shared_policy_id

# === Rebuild the Config ===
config = (
    PPOConfig()
    .environment(env="multi_agent_swarm_env")
    .framework("torch")
    .multi_agent(
        policies=policies,
        policy_mapping_fn=policy_mapping_fn,
    )
    # .resources(num_gpus=0)
    .rl_module(model_config={"fcnet_hiddens": [128, 128]})
)

# === Load from Checkpoint ===

checkpoint_folder = "ray_results/shared_policy_swarm_training/PPO_multi_agent_swarm_env_5c23e_00000_0_2025-05-28_11-15-55"
checkpoint_path = os.path.join(FOLDER, checkpoint_folder, "checkpoint_000000")
algo = PPO(config=config)
algo.restore(checkpoint_path)
module = algo.get_module("shared_policy")
module.eval()
env = SimWrapperEnv()

def learned_action(obs):
    with torch.inference_mode():
        obs_tensor = torch.tensor([obs], dtype=torch.float32)
        output = module.forward_inference({"obs": obs_tensor})
        mean    = output["action_dist_inputs"][0][:2]
        log_std = output["action_dist_inputs"][0][2:]
        std = torch.exp(log_std)
        dist = Normal(mean, std)
        action = dist.sample()
        action_clamped = torch.clamp(action, torch.tensor(env.action_space.low), torch.tensor(env.action_space.high))
        return action_clamped

def agents_observation(agents):
    observations = {}
    for agent in agents:
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

def animation_callback():
    global sim_obj
    global det_obj
    # tick   
    sim_obj.tick()
    # get detections and observations
    new_det = det_obj(sim_obj)
    new_obs = agents_observation(sim_obj.agents)
    # apply commands
    for name in new_det:
        agent = next((agent for agent in sim_obj.agents if agent.name == name), None)
        if agent == None: continue
        agent_obs = new_obs[name]
        action = learned_action(agent_obs)
        force, yawrate = action[0].item(), action[1].item()
        print(f'name: {name}, F: {force:2f}, YR : {yawrate:.2f}')
        agent.cmd_forces = force
        agent.cmd_yawrate = yawrate

if __name__ == "__main__":
# MAIN
    Animation.update_plot(callback=animation_callback)