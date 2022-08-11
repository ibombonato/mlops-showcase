import os

import wandb


def setup_tracker():
    """Setting up Wand for Tracking and Registry"""
    wandb.login(key=os.environ["WANDB_API_KEY"])
    run = wandb.init(project=os.environ["WANDB_PROJECT"])
    return run
