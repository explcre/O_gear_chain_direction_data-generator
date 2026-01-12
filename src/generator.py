"""
Gear Chain Direction Task Generator.

Generates chains of connected gears where adjacent gears rotate in opposite directions.
Task: Predict the rotation direction of the last gear given the first gear's direction.
"""

import random
import tempfile
import math
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """Gear chain direction prediction task generator."""
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
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
        
        prompt = get_prompt(task_data.get("type", "default"))
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def _generate_task_data(self) -> dict:
        """Generate gear chain configuration."""
        num_gears = random.randint(self.config.min_gears, self.config.max_gears)
        
        # First gear direction: True = clockwise, False = counterclockwise
        first_direction_cw = random.choice([True, False])
        
        # Calculate last gear direction (alternates with each gear)
        # If odd number of gears, last gear same as first
        # If even number of gears, last gear opposite to first
        last_direction_cw = first_direction_cw if (num_gears % 2 == 1) else not first_direction_cw
        
        # Generate gear positions (horizontal chain)
        width, height = self.config.image_size
        gear_radius = min(width, height) // (num_gears * 2 + 2)
        
        # Calculate spacing so gears touch (mesh)
        gear_spacing = gear_radius * 1.9  # Slightly less than 2r for visual overlap
        
        total_width = (num_gears - 1) * gear_spacing
        start_x = (width - total_width) // 2
        center_y = height // 2
        
        gears = []
        for i in range(num_gears):
            x = start_x + i * gear_spacing
            # Alternate direction for each gear
            is_cw = first_direction_cw if (i % 2 == 0) else not first_direction_cw
            gears.append({
                "x": x,
                "y": center_y,
                "radius": gear_radius,
                "clockwise": is_cw,
                "index": i
            })
        
        return {
            "gears": gears,
            "num_gears": num_gears,
            "first_direction_cw": first_direction_cw,
            "last_direction_cw": last_direction_cw,
            "type": "default"
        }
    
    def _draw_gear(self, draw: ImageDraw.Draw, x: int, y: int, radius: int, 
                   color: tuple, num_teeth: int = 12, rotation_angle: float = 0):
        """Draw a gear with teeth."""
        # Draw main gear body
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=color,
            outline=(50, 50, 50),
            width=2
        )
        
        # Draw teeth
        tooth_length = radius * 0.2
        for i in range(num_teeth):
            angle = rotation_angle + (2 * math.pi * i / num_teeth)
            inner_x = x + (radius - 5) * math.cos(angle)
            inner_y = y + (radius - 5) * math.sin(angle)
            outer_x = x + (radius + tooth_length) * math.cos(angle)
            outer_y = y + (radius + tooth_length) * math.sin(angle)
            
            draw.line([(inner_x, inner_y), (outer_x, outer_y)], fill=(50, 50, 50), width=4)
        
        # Draw center hole
        center_radius = radius * 0.15
        draw.ellipse(
            [x - center_radius, y - center_radius, x + center_radius, y + center_radius],
            fill=(50, 50, 50)
        )
    
    def _draw_rotation_arrow(self, draw: ImageDraw.Draw, x: int, y: int, 
                             radius: int, clockwise: bool, color: tuple):
        """Draw a curved arrow indicating rotation direction."""
        arrow_radius = radius * 0.6
        
        # Draw arc
        if clockwise:
            start_angle = -45
            end_angle = 135
        else:
            start_angle = 45
            end_angle = 225
        
        # Draw arc as series of lines
        num_segments = 20
        points = []
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = math.radians(start_angle + t * (end_angle - start_angle))
            px = x + arrow_radius * math.cos(angle)
            py = y + arrow_radius * math.sin(angle)
            points.append((px, py))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=4)
        
        # Draw arrowhead at the end
        end_angle_rad = math.radians(end_angle)
        arrow_tip_x = x + arrow_radius * math.cos(end_angle_rad)
        arrow_tip_y = y + arrow_radius * math.sin(end_angle_rad)
        
        # Arrowhead direction
        if clockwise:
            head_angle1 = end_angle_rad + math.radians(150)
            head_angle2 = end_angle_rad + math.radians(210)
        else:
            head_angle1 = end_angle_rad - math.radians(150)
            head_angle2 = end_angle_rad - math.radians(210)
        
        head_len = 15
        head1_x = arrow_tip_x + head_len * math.cos(head_angle1)
        head1_y = arrow_tip_y + head_len * math.sin(head_angle1)
        head2_x = arrow_tip_x + head_len * math.cos(head_angle2)
        head2_y = arrow_tip_y + head_len * math.sin(head_angle2)
        
        draw.polygon([(arrow_tip_x, arrow_tip_y), (head1_x, head1_y), (head2_x, head2_y)], fill=color)
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state with first gear's direction shown."""
        width, height = self.config.image_size
        img = Image.new('RGB', (width, height), self.config.bg_color)
        draw = ImageDraw.Draw(img)
        
        gears = task_data["gears"]
        
        # Draw all gears
        for gear in gears:
            self._draw_gear(draw, gear["x"], gear["y"], gear["radius"], self.config.gear_color)
        
        # Draw arrow only on first gear
        first_gear = gears[0]
        self._draw_rotation_arrow(
            draw, first_gear["x"], first_gear["y"],
            first_gear["radius"], first_gear["clockwise"],
            self.config.arrow_color
        )
        
        # Add question mark on last gear
        last_gear = gears[-1]
        draw.text(
            (last_gear["x"] - 10, last_gear["y"] - 15),
            "?",
            fill=(0, 0, 0)
        )
        
        return img
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state with last gear's direction highlighted."""
        width, height = self.config.image_size
        img = Image.new('RGB', (width, height), self.config.bg_color)
        draw = ImageDraw.Draw(img)
        
        gears = task_data["gears"]
        
        # Draw all gears
        for i, gear in enumerate(gears):
            # Highlight last gear
            if i == len(gears) - 1:
                self._draw_gear(draw, gear["x"], gear["y"], gear["radius"], self.config.highlight_color)
            else:
                self._draw_gear(draw, gear["x"], gear["y"], gear["radius"], self.config.gear_color)
        
        # Draw arrow on first gear
        first_gear = gears[0]
        self._draw_rotation_arrow(
            draw, first_gear["x"], first_gear["y"],
            first_gear["radius"], first_gear["clockwise"],
            self.config.arrow_color
        )
        
        # Draw arrow on last gear (answer)
        last_gear = gears[-1]
        self._draw_rotation_arrow(
            draw, last_gear["x"], last_gear["y"],
            last_gear["radius"], last_gear["clockwise"],
            self.config.highlight_color
        )
        
        return img
    
    def _generate_video(self, first_image: Image.Image, final_image: Image.Image,
                        task_id: str, task_data: dict) -> str:
        """Generate video showing gears rotating."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        frames = []
        num_frames = 30
        hold_frames = 5
        
        # Hold initial
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # Animation frames showing rotation
        gears = task_data["gears"]
        width, height = self.config.image_size
        
        for frame_idx in range(num_frames):
            img = Image.new('RGB', (width, height), self.config.bg_color)
            draw = ImageDraw.Draw(img)
            
            rotation_speed = 0.1
            
            for i, gear in enumerate(gears):
                # Calculate rotation angle
                direction = 1 if gear["clockwise"] else -1
                angle = direction * rotation_speed * frame_idx
                
                self._draw_gear(
                    draw, gear["x"], gear["y"], gear["radius"],
                    self.config.gear_color if i < len(gears) - 1 else self.config.highlight_color,
                    rotation_angle=angle
                )
            
            # Draw arrows
            first_gear = gears[0]
            self._draw_rotation_arrow(
                draw, first_gear["x"], first_gear["y"],
                first_gear["radius"], first_gear["clockwise"],
                self.config.arrow_color
            )
            
            last_gear = gears[-1]
            self._draw_rotation_arrow(
                draw, last_gear["x"], last_gear["y"],
                last_gear["radius"], last_gear["clockwise"],
                self.config.highlight_color
            )
            
            frames.append(img)
        
        # Hold final
        for _ in range(hold_frames):
            frames.append(final_image.copy())
        
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None
