import warnings
from enum import Enum
from typing import Any, List, Optional, Union

import pydantic
from pydantic import BaseModel

from app import config



warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Field name.*shadows an attribute in parent.*",
)


class VideoConcatMode(str, Enum):
    random = "random"
    sequential = "sequential"


class VideoAspect(str, Enum):
    landscape = "16:9"
    portrait = "9:16"
    square = "1:1"

    def to_resolution(self):
        if self == VideoAspect.landscape.value:
            return 1920, 1080
        elif self == VideoAspect.portrait.value:
            return 1080, 1920
        elif self == VideoAspect.square.value:
            return 1080, 1080
        return 1080, 1920


class _Config:
    arbitrary_types_allowed = True


@pydantic.dataclasses.dataclass(config=_Config)
class MaterialInfo:
    provider: str = "pexels"
    url: str = ""
    duration: int = 0


class VideoParams(BaseModel):
    video_aspect: Optional[VideoAspect] = VideoAspect.portrait.value
    voice_rate: Optional[float] = config["video"].get("voice_rate", 1.0)
    bgm_file: Optional[str] = config["video"].get("bgm", "")

    subtitle_enabled: Optional[bool] = True
    subtitle_position: Optional[str] = "custom"  # top, bottom, center
    custom_position: float = config["video"].get("subtitle_position", 70)

    text_fore_color: Optional[str] = config["video"].get("font_color", "#FFFFFF")
    text_background_color: Union[bool, str] = True

    font_size: int = config["video"].get("font_size", 60)
    stroke_color: Optional[str] = config["video"].get("stroke_color", "#000000")
    stroke_width: float = config["video"].get("stroke_width", 4)
    n_threads: Optional[int] = 2
    paragraph_number: Optional[int] = 1
