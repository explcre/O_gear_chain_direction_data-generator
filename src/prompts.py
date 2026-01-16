"""Gear Chain Direction Task Prompts - Precise version."""

def get_prompt(task_data: dict) -> str:
    """Generate a precise prompt that uniquely determines the video output.
    
    The prompt specifies:
    - Number of gears and their arrangement
    - First gear's rotation direction
    - The green tooth on each gear
    - The stopping condition (green teeth of last two gears meet)
    """
    num_gears = task_data["num_gears"]
    first_direction = task_data["first_direction"]
    last_direction = task_data["last_direction"]
    line_type = task_data["line_type"]
    
    line_desc = {
        "horizontal": "arranged horizontally in a row",
        "vertical": "arranged vertically in a column",
        "diagonal_down": "arranged diagonally from top-left to bottom-right",
        "diagonal_up": "arranged diagonally from bottom-left to top-right",
    }[line_type]
    
    prompt = f"""A chain of {num_gears} connected gears is {line_desc}.
Each gear has one GREEN colored tooth.

G1 (the first gear) rotates {first_direction} (shown by blue arrow).
Adjacent gears always rotate in OPPOSITE directions.

Animation requirements:
1. All gears rotate according to the direction rules
2. The rotation STOPS when the green teeth of the last two gears (G{num_gears-1} and G{num_gears}) meet exactly
3. At the end, G{num_gears}'s rotation direction is revealed with a blue arrow
4. G{num_gears} is highlighted when the answer is shown

What direction does G{num_gears} rotate? Show the gears rotating until the green teeth alignment stopping condition is met."""

    return prompt


def get_all_prompts() -> list[str]:
    """Return example prompts."""
    return [
        "Gear chain with green teeth. Gears rotate until green teeth of last two gears meet exactly."
    ]
