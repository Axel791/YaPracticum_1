import enum
from datetime import datetime
from typing import Optional

from schemas.mixins import TimeStampedMixin, UUIDMixin


class FilmType(enum.Enum):
    TV_SHOW = "tv_show"
    FILM = "movie"


class FilmWork(TimeStampedMixin, UUIDMixin):
    title: Optional[str]
    description: Optional[str]
    type: Optional[FilmType]
    creation_date: Optional[datetime]

    rating: Optional[float] = 0.0
