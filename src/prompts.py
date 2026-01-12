"""Gear Chain Direction Task Prompts."""

import random

PROMPTS = {
    "default": [
        "The first gear rotates as shown by the arrow. Predict and show the rotation direction of the last gear in the chain.",
        "Given the rotation direction of the first gear, determine which way the final gear will rotate. Adjacent gears rotate in opposite directions.",
        "Show the rotation direction of the last gear. Remember: connected gears rotate in opposite directions.",
    ],
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)

def get_all_prompts(task_type: str = "default") -> list[str]:
    return PROMPTS.get(task_type, PROMPTS["default"])
