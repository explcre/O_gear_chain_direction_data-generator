# src/prompts.py
"""Gear Chain Direction Task Prompts."""

import random

PROMPTS = {
    "default": [
        "Show the rotation direction of the last gear. Remember: connected gears rotate in opposite directions.",
        "Determine which way the final gear will rotate based on the chain of connected gears.",
        "Follow the gear chain and predict the rotation direction of the last gear marked with '?'.",
        "Adjacent gears rotate in opposite directions. What direction does the last gear rotate?",
        "Trace the rotation through the gear chain to find the final gear's direction.",
    ],
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)

def get_all_prompts(task_type: str = "default") -> list[str]:
    return PROMPTS.get(task_type, PROMPTS["default"])
