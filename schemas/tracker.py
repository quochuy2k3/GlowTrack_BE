from typing import List

from beanie import PydanticObjectId
from pydantic import BaseModel


class DayStatus(BaseModel):
    date: str
    isHasValue: bool
    tracker_id: list[str] = []
