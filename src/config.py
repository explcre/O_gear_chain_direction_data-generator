"""
Gear Chain Direction Task Configuration.
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Gear Chain Direction task configuration.
    
    Task: Given a chain of connected gears with the first gear's rotation direction,
    predict the rotation direction of the last gear.
    """
    
    domain: str = Field(default="gear_chain")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    generate_videos: bool = Field(default=True)
    video_fps: int = Field(default=10)
    
    # Task-specific settings
    min_gears: int = Field(default=3, description="Minimum number of gears in chain")
    max_gears: int = Field(default=7, description="Maximum number of gears in chain")
    
    gear_color: tuple[int, int, int] = Field(default=(100, 100, 100))
    arrow_color: tuple[int, int, int] = Field(default=(255, 50, 50))
    highlight_color: tuple[int, int, int] = Field(default=(50, 200, 50))
    bg_color: tuple[int, int, int] = Field(default=(255, 255, 255))
