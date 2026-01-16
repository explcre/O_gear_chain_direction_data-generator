# O-68: Gear Chain Direction Data Generator

## Task Description
Given a chain of connected gears with the first gear's rotation direction shown, predict the rotation direction of the last gear.

**Reasoning Type:** Physics/Mechanics - Alternating rotation propagation

## Visual Elements
- **Gears**: Circular gears with teeth arranged on a line (horizontal, vertical, or diagonal)
- **Green Tooth**: Each gear has one GREEN colored tooth for alignment reference
- **Rotation Arrows**: Blue curved arrows showing rotation direction
- **Gear Labels**: G1, G2, G3... labels below each gear

## Task Logic
Adjacent gears rotate in **opposite directions**:
- If G1 rotates clockwise → G2 rotates counterclockwise → G3 rotates clockwise...
- Odd number of gears: last gear same direction as first
- Even number of gears: last gear opposite direction from first

## Output Format
```
data/questions/gear_chain_task/{task_id}/
├── first_frame.png      # Gears with G1's direction shown, last gear has "?"
├── final_frame.png      # All directions revealed, last gear highlighted
├── prompt.txt           # Precise task description
└── ground_truth.mp4     # Animation showing rotation until green teeth meet
```

## Animation Sequence
1. Initial state with first gear's direction shown
2. All gears rotate according to direction rules
3. Rotation stops when green teeth of last two gears meet exactly
4. Last gear's direction revealed with blue arrow
5. Last gear highlighted

## Usage
```bash
python examples/generate.py --num-samples 100 --seed 42
```

### Parameters
- `--num-samples N`: Number of tasks to generate (required)
- `--output DIR`: Output directory (default: data/questions)  
- `--seed N`: Random seed for reproducibility
- `--no-videos`: Skip video generation

## Configuration
Edit `src/config.py` to customize:
- `min_gears` / `max_gears`: Chain length range (default: 3-6)
- `gear_radius`: Size of gears (default: 40px)
- `gear_gap`: Spacing between gears (default: 15px)

## Sample Prompt
```
A chain of 4 connected gears is arranged horizontally in a row.
Each gear has one GREEN colored tooth.
G1 (the first gear) rotates clockwise (shown by blue arrow).
Adjacent gears always rotate in OPPOSITE directions.
...
```
