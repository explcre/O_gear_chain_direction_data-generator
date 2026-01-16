# O-68: Gear Chain Direction Data Generator

## Task Description
Given a chain of connected gears with the first gear's rotation direction shown, predict the rotation direction of the last gear.

**Reasoning Type:** Physics/Mechanics - Alternating rotation propagation through meshing gears

## Visual Elements
- **Gears**: Circular gears with teeth arranged on a line (horizontal, vertical, or diagonal)
- **Realistic Meshing**: Gears positioned close together with teeth appearing to interlock
- **Green Tooth**: Each gear has one GREEN colored tooth for alignment reference
- **Rotation Arrows**: Blue curved arrows showing rotation direction
- **Gear Labels**: G1, G2, G3... labels below each gear

## Key Features
### Realistic Gear Meshing
- Gears are positioned with minimal gap (configurable, default: -8px creates overlap)
- Teeth appear to interlock between adjacent gears
- Initial angles are calculated to prevent any teeth overlap
- Enhanced collision detection ensures no teeth collide in the first frame
- Visual appearance suggests mechanical force transmission

### Collision Prevention
- Sophisticated tooth position calculation
- Checks distance between all tooth tips of adjacent gears
- Automatic angle adjustment to eliminate overlaps
- Fine-grained angle refinement for perfect meshing

## Task Logic
Adjacent gears rotate in **opposite directions** due to meshing:
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
1. Initial state with first gear's direction shown, gears in meshing positions with zero teeth overlap
2. All gears rotate according to direction rules (maintaining mesh appearance)
3. Rotation stops at FIRST TIME when green teeth of last two gears are 180 degrees apart
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
- `gear_gap`: Spacing between gears (default: -8px for realistic meshing)
  - Negative values create overlap/meshing appearance
  - Positive values create gaps between gears
  - Zero means gears just touch

## Technical Improvements

### Enhanced Meshing Algorithm
The generator now implements:
1. **Strategic Initial Positioning**: First gear gets random angle, subsequent gears are positioned with half-tooth offset for natural meshing
2. **Precise Collision Detection**: 
   - Calculates exact tooth tip positions for all teeth
   - Checks distances between facing teeth only
   - Uses safety margin (1.5x tooth width) to prevent any overlap
3. **Iterative Refinement**: 
   - Fine angle adjustments (1/8 tooth angle steps)
   - Up to 200 iterations per gear pair
   - Falls back to adjusting previous gear if needed

### Spacing Calculation
- Formula: `spacing = gear_radius * 2 + tooth_length * 2 + gear_gap`
- Default: `40 * 2 + 15 * 2 + (-8) = 102px center-to-center`
- This creates realistic meshing where teeth just interlock

## Sample Prompt
```
A chain of 4 connected gears is arranged horizontally in a row.
The gears are positioned CLOSE TOGETHER to create a realistic meshing appearance.
Each gear has exactly 12 teeth and one GREEN colored tooth.
G1 (the first gear) rotates clockwise (shown by blue arrow).
Adjacent gears ALWAYS rotate in OPPOSITE directions (due to meshing).
Animation stops at FIRST TIME when green teeth of last two gears are 180 degrees apart.
...
```

## Dependencies
See `requirements.txt`:
- numpy==1.26.4
- Pillow==10.4.0
- pydantic==2.10.5
- opencv-python==4.10.0.84 (for video generation)
