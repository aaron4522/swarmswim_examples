import numpy as np
import os

import ray
from ray.tune import CheckpointConfig
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.callbacks import DefaultCallbacks

from marl_env import SimWrapperEnv

FOLDER = os.path.dirname(os.path.abspath(__file__)) 

# --- Register the environment ---

def env_creator(config):
    return SimWrapperEnv()

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

class LogCallbacks(DefaultCallbacks):
    def on_episode_end(self, *, episode, env_runner, metrics_logger,
        env, env_index, rl_module, **kwargs, ) -> None:
        # Retrieve the latest rewards for all agents
        rewards_dict = episode.get_rewards()
        total_episode_reward = 0
        
        for agent_id, elem in rewards_dict.items():
            metrics_logger.log_value(f"episode_len/{agent_id}",len(elem))
            reward = elem[-1]
            metrics_logger.log_value(f"reward/{agent_id}",reward)
            total_episode_reward+=reward
    
        # Log total episode reward
        metrics_logger.log_value("reward/total", total_episode_reward)
            
    def on_checkpoint(self, algorithm, checkpoint, **kwargs):
        print(f"Checkpoint saved: {checkpoint.path}")


# --- Updated config ---

config = (
    PPOConfig()
    .environment(env="multi_agent_swarm_env")
    .framework("torch")
    .training(
        train_batch_size_per_learner=256,
        gamma=0.97,
        lr=5e-4,
        # model={"fcnet_hiddens": [128, 128]}
    )
    .multi_agent(
        policies=policies,
        policy_mapping_fn=policy_mapping_fn,
    )
    .rl_module(model_config={
        "fcnet_hiddens": [128, 128],
        "fcnet_activation": "relu"})
    .env_runners(
        num_env_runners=4,     
        num_envs_per_env_runner=8, 
        env_runner_cls=None,
        num_cpus_per_env_runner=7
    )
    .resources()
    .callbacks(LogCallbacks)
)

# --- Run training ---
if __name__ == "__main__":
    ray.init()
    print(ray.available_resources())

    ray.tune.Tuner(
        "PPO",
        param_space=config.to_dict(),
        run_config=ray.tune.RunConfig(
            stop={"training_iteration": 10000},
            storage_path=FOLDER+"/ray_results",
            name="shared_policy_swarm_training",
        #     checkpoint_config=CheckpointConfig(
        #         checkpoint_score_attribute="env_runners/reward/total",
        #         checkpoint_score_order="max",         # or "min"
        #         checkpoint_frequency=10,
        #         num_to_keep=3,                        # Only keep the best one
        # ),
        ),
    ).fit()
