"""Gear Chain Direction Task Prompts - Ultra-detailed version with meeting condition."""


def get_prompt(task_data: dict) -> str:
    """Generate an extremely detailed prompt that precisely describes every visual element and animation frame."""
    num_gears = task_data["num_gears"]
    first_direction = task_data["first_direction"]
    last_direction = task_data["last_direction"]
    line_type = task_data["line_type"]
    gears = task_data["gears"]
    green_indices = task_data["green_tooth_indices"]

    line_desc = {
        "horizontal": "arranged horizontally in a straight row from left to right",
        "vertical": "arranged vertically in a straight column from top to bottom",
        "diagonal_down": "arranged diagonally from top-left to bottom-right",
        "diagonal_up": "arranged diagonally from bottom-left to top-right",
    }[line_type]

    # Calculate connection angle between last two gears
    import math

    if num_gears >= 2:
        gear_last = gears[num_gears - 1]
        gear_second_last = gears[num_gears - 2]
        dx = gear_last["x"] - gear_second_last["x"]
        dy = gear_last["y"] - gear_second_last["y"]
        connection_angle_rad = math.atan2(dy, dx)
        connection_angle_deg = math.degrees(connection_angle_rad) % 360
    else:
        connection_angle_deg = 0

    # Describe each gear's position
    gear_positions = []
    for i, gear in enumerate(gears):
        gear_positions.append(
            f"  G{i+1}: center at pixel ({gear['x']}, {gear['y']}), radius 40px"
        )

    positions_str = "\n".join(gear_positions)

    # Describe green tooth positions
    green_desc = []
    for i, idx in enumerate(green_indices):
        green_desc.append(
            f"  G{i+1}: green tooth at index {idx} out of 12 teeth (index 0 = rightmost tooth)"
        )

    greens_str = "\n".join(green_desc)

    prompt = f"""INITIAL STATE (Frame 0):

SCENE DESCRIPTION:
A chain of {num_gears} circular gears {line_desc} on a white background RGB(255,255,255).

GEAR SPECIFICATIONS:
Each gear consists of:
- Circular body: radius 40 pixels, center hole radius 8 pixels
- Body color: light gray RGB(180,180,180)
- Center hole color: dark gray RGB(80,80,80)
- Outline: medium gray RGB(100,100,100), 2 pixels wide
- Exactly 12 teeth evenly spaced around circumference (30° apart)
- Normal teeth: gray RGB(120,120,120) with dark outline RGB(80,80,80)
- ONE green tooth per gear: bright green RGB(50,200,50) with dark outline
- Each tooth: rectangular trapezoid, length 15px, width 8px at base

GEAR POSITIONS AND LABELS:
{positions_str}

Each gear has a label below it:
- Text: "G1", "G2", ... "G{num_gears}"
- Position: 20 pixels below gear center
- Font: regular, size 14
- Color: gray RGB(100,100,100)

GREEN TOOTH CONFIGURATION:
{greens_str}

Tooth indexing: 0=rightmost (0°), 3=top (90°), 6=leftmost (180°), 9=bottom (270°)

CONNECTION BETWEEN LAST TWO GEARS:
- G{num_gears-1} center: ({gears[num_gears-2]['x']}, {gears[num_gears-2]['y']})
- G{num_gears} center: ({gears[num_gears-1]['x']}, {gears[num_gears-1]['y']})
- Line connecting centers has angle: {connection_angle_deg:.1f}° from positive x-axis
- Gears are positioned {int(math.sqrt((gears[num_gears-1]['x']-gears[num_gears-2]['x'])**2 + (gears[num_gears-1]['y']-gears[num_gears-2]['y'])**2))} pixels apart (center to center)

ROTATION DIRECTION RULES:
- G1 (first gear) rotates {first_direction}
- Adjacent gears ALWAYS rotate in OPPOSITE directions
- G1: {first_direction}
- G2: {"counterclockwise" if first_direction == "clockwise" else "clockwise"}
"""

    for i in range(2, num_gears):
        if i % 2 == 0:
            dir_i = first_direction
        else:
            dir_i = (
                "counterclockwise" if first_direction == "clockwise" else "clockwise"
            )
        prompt += f"- G{i+1}: {dir_i}\n"

    prompt += f"""
Therefore: G{num_gears} (last gear) rotates {last_direction}

INITIAL STATE VISUAL ELEMENTS:
- All {num_gears} gears visible with their 12 teeth and one green tooth each
- G1 has a BLUE curved rotation arrow showing {first_direction} direction:
  Arrow properties:
  - Arc from -60° to 60° (clockwise) or 120° to 240° (counterclockwise)
  - Radius: 20 pixels from gear center
  - Line color: RGB(50,50,200), width 3 pixels
  - Arrowhead: filled triangle, 12 pixels long
  
- G{num_gears} has a RED question mark "?" at its center:
  - Font: bold, size 24
  - Color: RGB(200,50,50)
  - Position: center of G{num_gears}

- Text at top-left corner (10, 10):
  "G1 rotates {first_direction}"
  Font: bold, size 14
  Color: dark blue RGB(50,50,150)

- Text at (10, 30):
  "Green tooth on each gear"
  Font: bold, size 14
  Color: green RGB(50,150,50)

ANIMATION STOPPING CONDITION:
The animation STOPS when the green teeth of G{num_gears-1} and G{num_gears} MEET.

Meeting condition (all must be true):
1. The green tooth of G{num_gears-1} points TOWARD G{num_gears}
   (tooth angle matches connection line angle {connection_angle_deg:.1f}° ± 3°)
   
2. The green tooth of G{num_gears} points TOWARD G{num_gears-1}
   (tooth angle matches connection line angle + 180° = {(connection_angle_deg + 180) % 360:.1f}° ± 3°)
   
3. This means the two green teeth are on opposite ends of the connecting line,
   pointing at each other, essentially TOUCHING at the mesh point between gears.

Mathematical formulation:
- Let θ_conn = {connection_angle_deg:.1f}° (angle of line from G{num_gears-1} to G{num_gears})
- Let θ_G{num_gears-1} = angle of green tooth on G{num_gears-1} (measured from +x axis)
- Let θ_G{num_gears} = angle of green tooth on G{num_gears} (measured from +x axis)
- STOP when: |θ_G{num_gears-1} - θ_conn| < 3° AND |θ_G{num_gears} - (θ_conn + 180°)| < 3°

ANIMATION SEQUENCE (Total: 64 frames at 10 FPS):

FRAMES 1-8: Hold initial state
- All gears stationary
- G1 shows blue rotation arrow
- G{num_gears} shows red "?" question mark
- All green teeth visible at their initial angles

FRAMES 9-48: Rotation animation (40 frames)
All gears rotate simultaneously according to their directions:
- Gears with even indices (G1, G3, G5...): rotate {first_direction}
- Gears with odd indices (G2, G4, G6...): rotate {"counterclockwise" if first_direction == "clockwise" else "clockwise"}
- Rotation is smooth and continuous
- Frame rate: 10 FPS
- Angular velocity: constant

Each frame, check the stopping condition:
- Calculate green tooth angle for G{num_gears-1}
- Calculate green tooth angle for G{num_gears}
- If both are on the connecting line (within 3° tolerance), STOP

AT FRAME ~28 (70% progress):
- Blue curved rotation arrows appear on ALL gears (except G{num_gears}):
  Each arrow shows that gear's rotation direction
  - G1: already has arrow (remains)
  - G2 through G{num_gears-1}: new arrows appear
  - Arrow specifications: RGB(50,50,200), 3px wide, with triangular arrowhead
  
- G{num_gears} still shows "?" question mark

AT FRAME ~43 (90% progress):
- G{num_gears} changes appearance:
  Body color changes to light green RGB(200,220,200) - HIGHLIGHTED
  "?" question mark is REMOVED
  Blue rotation arrow appears showing {last_direction} direction
  
- Text appears at bottom (10, 470):
  "Green teeth meet - STOP"
  Font: bold, size 12
  Color: green RGB(50,150,50)

FINAL STATE (Frame 48):
- All gears stopped at the moment when:
  G{num_gears-1}'s green tooth angle = {connection_angle_deg:.1f}° (pointing toward G{num_gears})
  G{num_gears}'s green tooth angle = {(connection_angle_deg + 180) % 360:.1f}° (pointing toward G{num_gears-1})
  
- G{num_gears} is highlighted in light green RGB(200,220,200)

- All gears show blue rotation direction arrows RGB(50,50,200):
  G1, G3, G5... show {first_direction} arrows
  G2, G4, G6... show {"counterclockwise" if first_direction == "clockwise" else "clockwise"} arrows

- Text at top (10, 10):
  "G{num_gears} rotates {last_direction}"
  Font: bold, size 14
  Color: green RGB(50,150,50)

- Text at (10, 30):
  "Green teeth meet on connecting line!"
  Font: bold, size 14
  Color: green RGB(50,150,50)

- Gear labels G1...G{num_gears} remain visible below each gear

FRAMES 49-64: Hold final state (16 frames)

LAYER ORDERING (bottom to top):
1. White background RGB(255,255,255)
2. Gear bodies (gray or light green)
3. Center holes (dark gray)
4. Gear teeth (gray or green)
5. Rotation arrows (blue)
6. Question mark or text labels
7. Text annotations

CRITICAL COLOR SPECIFICATIONS:
- Background: RGB(255,255,255) white
- Gear body (normal): RGB(180,180,180) light gray
- Gear body (highlighted): RGB(200,220,200) light green
- Gear outline: RGB(100,100,100) medium gray, 2px
- Center hole: RGB(80,80,80) dark gray
- Normal teeth: RGB(120,120,120) gray with RGB(80,80,80) outline
- Green teeth: RGB(50,200,50) bright green with RGB(80,80,80) outline
- Rotation arrows: RGB(50,50,200) blue, 3px wide
- Question mark: RGB(200,50,50) red, size 24, bold
- Labels (G1, G2...): RGB(100,100,100) gray, size 14
- Top text (initial): RGB(50,50,150) dark blue
- Top text (final): RGB(50,150,50) green
- Bottom text (stop message): RGB(50,150,50) green

PHYSICAL INTERPRETATION:
When the animation stops, the green teeth are positioned such that:
- They lie on the straight line connecting the two gear centers
- They are 180° apart (on opposite sides of the connecting line)
- They are essentially TOUCHING/MEETING at the point where the gears mesh
- This represents the moment when these two specific teeth align perfectly

ANSWER: G{num_gears} rotates {last_direction}, and the animation stops when its green tooth meets the green tooth of G{num_gears-1} on their connecting line."""

    return prompt


def get_all_prompts() -> list[str]:
    return [
        "Gear chain with green teeth. Gears rotate until green teeth of last two gears meet on their connecting line."
    ]
