"""
Gear Chain Direction Task Generator.

Generates gear chains where adjacent gears rotate in opposite directions.
Task: Given the first gear's rotation direction, predict the last gear's direction.

Features:
- Gears arranged on various line orientations (horizontal, vertical, diagonal)
- Each gear has one GREEN colored tooth
- TOOTH OVERLAP PREVENTION: Algorithm ensures no teeth overlap in initial frame
- Video stops when green teeth of last two gears meet
"""

import random
import tempfile
import math
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """Gear chain direction task generator."""
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        self.num_teeth = 12  # Fixed number of teeth per gear
        
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair."""
        task_data = self._generate_task_data()
        
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        prompt = get_prompt(task_data)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def _generate_task_data(self) -> dict:
        """Generate gear chain configuration with no tooth overlap."""
        num_gears = random.randint(self.config.min_gears, self.config.max_gears)
        
        # First gear rotation direction
        first_direction = random.choice(["clockwise", "counterclockwise"])
        
        # Calculate last gear direction (alternates each gear)
        if num_gears % 2 == 1:
            last_direction = first_direction
        else:
            last_direction = "counterclockwise" if first_direction == "clockwise" else "clockwise"
        
        # Choose arrangement line type
        line_types = ["horizontal", "vertical", "diagonal_down", "diagonal_up"]
        line_type = random.choice(line_types)
        
        # Generate gear positions along the line
        width, height = self.config.image_size
        gear_radius = self.config.gear_radius
        tooth_length = 15
        # Spacing must account for teeth on both gears
        gear_spacing = gear_radius * 2 + tooth_length * 2 + self.config.gear_gap
        
        gears = []
        
        if line_type == "horizontal":
            total_width = (num_gears - 1) * gear_spacing
            start_x = (width - total_width) // 2
            for i in range(num_gears):
                x = start_x + i * gear_spacing
                y = height // 2
                gears.append({"x": x, "y": y, "radius": gear_radius})
        
        elif line_type == "vertical":
            total_height = (num_gears - 1) * gear_spacing
            start_y = (height - total_height) // 2
            for i in range(num_gears):
                x = width // 2
                y = start_y + i * gear_spacing
                gears.append({"x": x, "y": y, "radius": gear_radius})
        
        elif line_type == "diagonal_down":
            spacing_xy = gear_spacing / math.sqrt(2)
            total_diag = (num_gears - 1) * spacing_xy
            start_x = (width - total_diag) // 2
            start_y = (height - total_diag) // 2
            for i in range(num_gears):
                x = start_x + i * spacing_xy
                y = start_y + i * spacing_xy
                gears.append({"x": int(x), "y": int(y), "radius": gear_radius})
        
        else:  # diagonal_up
            spacing_xy = gear_spacing / math.sqrt(2)
            total_diag = (num_gears - 1) * spacing_xy
            start_x = (width - total_diag) // 2
            start_y = (height + total_diag) // 2
            for i in range(num_gears):
                x = start_x + i * spacing_xy
                y = start_y - i * spacing_xy
                gears.append({"x": int(x), "y": int(y), "radius": gear_radius})
        
        # Assign rotation directions (alternating)
        directions = []
        for i in range(num_gears):
            if i % 2 == 0:
                directions.append(first_direction)
            else:
                directions.append("counterclockwise" if first_direction == "clockwise" else "clockwise")
        
        # Initialize rotation angles and ensure no tooth overlap
        rotation_angles = self._initialize_angles_no_overlap(gears, line_type)
        
        # Assign green tooth angle for each gear (one tooth per gear)
        green_tooth_indices = [random.randint(0, self.num_teeth - 1) for _ in range(num_gears)]
        
        return {
            "num_gears": num_gears,
            "gears": gears,
            "directions": directions,
            "first_direction": first_direction,
            "last_direction": last_direction,
            "line_type": line_type,
            "rotation_angles": rotation_angles,
            "green_tooth_indices": green_tooth_indices,
        }
    
    def _initialize_angles_no_overlap(self, gears: List[dict], line_type: str) -> List[float]:
        """Initialize gear rotation angles ensuring no teeth overlap between adjacent gears."""
        num_gears = len(gears)
        angles = [random.uniform(0, 2 * math.pi) for _ in range(num_gears)]
        
        # Get the direction from gear i to gear i+1
        def get_connection_angle(g1: dict, g2: dict) -> float:
            dx = g2["x"] - g1["x"]
            dy = g2["y"] - g1["y"]
            return math.atan2(dy, dx)
        
        # Check if teeth would overlap between two gears
        def teeth_overlap(gear1: dict, angle1: float, gear2: dict, angle2: float) -> bool:
            """Check if any tooth from gear1 overlaps with any tooth from gear2."""
            radius = self.config.gear_radius
            tooth_length = 15
            tooth_width = 8
            
            # Get all tooth tip positions for both gears
            teeth1 = []
            teeth2 = []
            
            for i in range(self.num_teeth):
                tooth_angle1 = angle1 + (2 * math.pi * i / self.num_teeth)
                tip_x1 = gear1["x"] + (radius + tooth_length) * math.cos(tooth_angle1)
                tip_y1 = gear1["y"] + (radius + tooth_length) * math.sin(tooth_angle1)
                teeth1.append((tip_x1, tip_y1, tooth_angle1))
                
                tooth_angle2 = angle2 + (2 * math.pi * i / self.num_teeth)
                tip_x2 = gear2["x"] + (radius + tooth_length) * math.cos(tooth_angle2)
                tip_y2 = gear2["y"] + (radius + tooth_length) * math.sin(tooth_angle2)
                teeth2.append((tip_x2, tip_y2, tooth_angle2))
            
            # Check for overlap - teeth are close to each other in the contact zone
            connection_angle = get_connection_angle(gear1, gear2)
            
            for t1 in teeth1:
                # Check if this tooth points toward gear2
                angle_to_g2 = math.atan2(gear2["y"] - gear1["y"], gear2["x"] - gear1["x"])
                tooth_dir_diff = abs((t1[2] - angle_to_g2 + math.pi) % (2 * math.pi) - math.pi)
                if tooth_dir_diff > math.pi / 3:  # Not pointing toward other gear
                    continue
                    
                for t2 in teeth2:
                    # Check if this tooth points toward gear1
                    angle_to_g1 = math.atan2(gear1["y"] - gear2["y"], gear1["x"] - gear2["x"])
                    tooth_dir_diff2 = abs((t2[2] - angle_to_g1 + math.pi) % (2 * math.pi) - math.pi)
                    if tooth_dir_diff2 > math.pi / 3:
                        continue
                    
                    # Check distance between tooth tips
                    dist = math.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)
                    if dist < tooth_width * 2:  # Overlap threshold
                        return True
            
            return False
        
        # Adjust angles to prevent overlap
        max_iterations = 100
        angle_step = 2 * math.pi / self.num_teeth / 4  # Small rotation step
        
        for i in range(num_gears - 1):
            gear1 = gears[i]
            gear2 = gears[i + 1]
            
            iteration = 0
            while teeth_overlap(gear1, angles[i], gear2, angles[i + 1]) and iteration < max_iterations:
                # Rotate gear i+1 slightly
                angles[i + 1] += angle_step
                if angles[i + 1] > 2 * math.pi:
                    angles[i + 1] -= 2 * math.pi
                iteration += 1
            
            # If still overlapping after max iterations, try adjusting gear i instead
            if iteration >= max_iterations:
                iteration = 0
                while teeth_overlap(gear1, angles[i], gear2, angles[i + 1]) and iteration < max_iterations:
                    angles[i] += angle_step
                    if angles[i] > 2 * math.pi:
                        angles[i] -= 2 * math.pi
                    iteration += 1
        
        return angles
    
    def _draw_gear(self, draw: ImageDraw.Draw, x: int, y: int, radius: int,
                   rotation_angle: float = 0, green_tooth_index: int = 0,
                   show_direction: bool = False, direction: str = "clockwise",
                   show_question: bool = False, highlight: bool = False):
        """Draw a single gear with teeth, one green tooth, and optional direction arrow."""
        
        # Gear body
        body_color = (180, 180, 180) if not highlight else (200, 220, 200)
        draw.ellipse([x - radius + 10, y - radius + 10, x + radius - 10, y + radius - 10],
                    fill=body_color, outline=(100, 100, 100), width=2)
        
        # Center hole
        hole_radius = radius // 5
        draw.ellipse([x - hole_radius, y - hole_radius, x + hole_radius, y + hole_radius],
                    fill=(80, 80, 80))
        
        # Draw teeth
        tooth_length = 15
        tooth_width = 8
        
        for i in range(self.num_teeth):
            angle = rotation_angle + (2 * math.pi * i / self.num_teeth)
            
            # Check if this is the green tooth
            is_green = (i == green_tooth_index)
            tooth_color = (50, 200, 50) if is_green else (120, 120, 120)
            
            # Tooth base position (at gear edge)
            base_x = x + (radius - 5) * math.cos(angle)
            base_y = y + (radius - 5) * math.sin(angle)
            
            # Tooth tip position
            tip_x = x + (radius + tooth_length) * math.cos(angle)
            tip_y = y + (radius + tooth_length) * math.sin(angle)
            
            # Calculate perpendicular direction for tooth width
            perp_angle = angle + math.pi / 2
            half_width = tooth_width / 2
            
            points = [
                (base_x - half_width * math.cos(perp_angle), base_y - half_width * math.sin(perp_angle)),
                (base_x + half_width * math.cos(perp_angle), base_y + half_width * math.sin(perp_angle)),
                (tip_x + half_width * math.cos(perp_angle), tip_y + half_width * math.sin(perp_angle)),
                (tip_x - half_width * math.cos(perp_angle), tip_y - half_width * math.sin(perp_angle)),
            ]
            draw.polygon(points, fill=tooth_color, outline=(80, 80, 80))
        
        # Draw direction arrow
        if show_direction:
            self._draw_rotation_arrow(draw, x, y, radius - 20, direction)
        
        # Draw question mark for last gear in initial state
        if show_question:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                font = ImageFont.load_default()
            draw.text((x - 8, y - 15), "?", fill=(200, 50, 50), font=font)
    
    def _draw_rotation_arrow(self, draw: ImageDraw.Draw, cx: int, cy: int, 
                             radius: int, direction: str):
        """Draw a curved rotation arrow with properly aligned triangle."""
        if direction == "clockwise":
            start_angle = -60
            end_angle = 60
        else:
            start_angle = 120
            end_angle = 240
        
        # Draw arc using line segments
        arc_points = []
        for angle_deg in range(start_angle, end_angle + 1, 5):
            angle = math.radians(angle_deg)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            arc_points.append((px, py))
        
        if len(arc_points) > 1:
            draw.line(arc_points, fill=(50, 50, 200), width=3)
        
        # Draw arrowhead at the end of the arc
        end_angle_rad = math.radians(end_angle)
        arrow_x = cx + radius * math.cos(end_angle_rad)
        arrow_y = cy + radius * math.sin(end_angle_rad)
        
        # Calculate tangent direction at arrow point
        if direction == "clockwise":
            tangent_angle = end_angle_rad + math.pi / 2
        else:
            tangent_angle = end_angle_rad - math.pi / 2
        
        # Arrow triangle with midpoint of base on curve
        arrow_size = 12
        tip_x = arrow_x + arrow_size * math.cos(tangent_angle)
        tip_y = arrow_y + arrow_size * math.sin(tangent_angle)
        
        perp_angle = tangent_angle + math.pi / 2
        base1_x = arrow_x + (arrow_size * 0.6) * math.cos(perp_angle)
        base1_y = arrow_y + (arrow_size * 0.6) * math.sin(perp_angle)
        base2_x = arrow_x - (arrow_size * 0.6) * math.cos(perp_angle)
        base2_y = arrow_y - (arrow_size * 0.6) * math.sin(perp_angle)
        
        draw.polygon([(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)], 
                    fill=(50, 50, 200))
    
    def _render_gears(self, task_data: dict, show_all_directions: bool = False,
                      show_question_on_last: bool = False, rotation_offset: float = 0,
                      highlight_last: bool = False) -> Image.Image:
        """Render all gears in the chain."""
        width, height = self.config.image_size
        img = Image.new('RGB', (width, height), self.config.bg_color)
        draw = ImageDraw.Draw(img)
        
        gears = task_data["gears"]
        directions = task_data["directions"]
        base_angles = task_data["rotation_angles"]
        green_indices = task_data["green_tooth_indices"]
        num_gears = task_data["num_gears"]
        
        for i, gear in enumerate(gears):
            is_first = (i == 0)
            is_last = (i == num_gears - 1)
            
            # Calculate rotation for this gear
            # Alternate direction of rotation offset (adjacent gears rotate opposite)
            if i % 2 == 0:
                gear_rotation = base_angles[i] + rotation_offset
            else:
                gear_rotation = base_angles[i] - rotation_offset
            
            # Show direction: always for first, optionally for others
            show_dir = is_first or (show_all_directions and not show_question_on_last) or \
                       (show_all_directions and not is_last)
            show_q = show_question_on_last and is_last
            highlight = highlight_last and is_last
            
            self._draw_gear(
                draw, gear["x"], gear["y"], gear["radius"],
                rotation_angle=gear_rotation,
                green_tooth_index=green_indices[i],
                show_direction=show_dir,
                direction=directions[i],
                show_question=show_q,
                highlight=highlight
            )
        
        # Draw gear numbers
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        for i, gear in enumerate(gears):
            label = f"G{i+1}"
            draw.text((gear["x"] - 10, gear["y"] + gear["radius"] + 20), 
                     label, fill=(100, 100, 100), font=font)
        
        return img
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state with question mark on last gear."""
        img = self._render_gears(task_data, show_all_directions=False, 
                                show_question_on_last=True)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        direction = task_data["first_direction"]
        draw.text((10, 10), f"G1 rotates {direction}", fill=(50, 50, 150), font=font)
        draw.text((10, 30), "Green tooth on each gear", fill=(50, 150, 50), font=font)
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state with all directions shown and last gear highlighted."""
        img = self._render_gears(task_data, show_all_directions=True, 
                                show_question_on_last=False, highlight_last=True)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        num_gears = task_data["num_gears"]
        last_dir = task_data["last_direction"]
        draw.text((10, 10), f"G{num_gears} rotates {last_dir}", fill=(50, 150, 50), font=font)
        draw.text((10, 30), "Green teeth of last two gears aligned!", fill=(50, 150, 50), font=font)
        
        return img
    
    def _generate_video(self, first_image: Image.Image, final_image: Image.Image,
                        task_id: str, task_data: dict) -> str:
        """Generate video showing gears rotating until green teeth meet."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        frames = []
        hold_frames = 8
        rotation_frames = 40
        
        # Hold initial
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # Animate rotation
        total_rotation = math.pi / 3
        
        for i in range(rotation_frames):
            progress = i / (rotation_frames - 1)
            rotation = total_rotation * progress
            
            img = self._render_gears(
                task_data, 
                show_all_directions=(progress > 0.7),
                show_question_on_last=(progress < 0.7),
                rotation_offset=rotation,
                highlight_last=(progress > 0.9)
            )
            
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            if progress > 0.9:
                draw.text((10, 470), "Green teeth aligned - STOP", fill=(50, 150, 50), font=font)
            
            frames.append(img)
        
        # Hold final
        for _ in range(hold_frames * 2):
            frames.append(final_image.copy())
        
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None
