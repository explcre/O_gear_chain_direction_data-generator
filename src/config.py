"""
Gear Chain Direction Task Configuration.
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Gear Chain Direction task configuration.
    
    Task: Given a chain of connected gears and the first gear's rotation,
    determine the rotation direction of the last gear.
    """
    
    domain: str = Field(default="gear_chain")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    generate_videos: bool = Field(default=True)
    video_fps: int = Field(default=10)
    
    # Gear chain settings - UPDATED FOR REALISTIC MESHING
    min_gears: int = Field(default=3, description="Minimum number of gears")
    max_gears: int = Field(default=6, description="Maximum number of gears")
    gear_radius: int = Field(default=40, description="Radius of each gear")
    gear_gap: int = Field(default=-8, description="Gap between adjacent gears (negative creates meshing)")
    
    # Colors
    bg_color: tuple[int, int, int] = Field(default=(255, 255, 255))
    gear_color: tuple[int, int, int] = Field(default=(180, 180, 180))
    tooth_color: tuple[int, int, int] = Field(default=(120, 120, 120))
    green_tooth_color: tuple[int, int, int] = Field(default=(50, 200, 50))
    arrow_color: tuple[int, int, int] = Field(default=(50, 50, 200))
