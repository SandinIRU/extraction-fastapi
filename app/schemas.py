from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, conint


class ItineraryExtractRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Unstructured travel request text")
    max_days: conint(ge=1, le=21) = 10
    currency: str = Field(default="LKR", description="Short currency code like LKR, USD")


class ActivityBlock(BaseModel):
    title: str = Field(..., min_length=2)
    details: Optional[str] = None
    place: Optional[str] = None
    estimated_cost: Optional[int] = Field(default=None, ge=0)


class DayPlan(BaseModel):
    day_number: conint(ge=1, le=21)
    base_city: str = Field(..., min_length=2)
    morning: List[ActivityBlock] = Field(default_factory=list)
    afternoon: List[ActivityBlock] = Field(default_factory=list)
    evening: List[ActivityBlock] = Field(default_factory=list)
    accommodation: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class Itinerary(BaseModel):
    trip_title: str = Field(..., min_length=3)
    traveler_count: conint(ge=1, le=20) = 1
    duration_days: conint(ge=1, le=21)
    currency: str = "LKR"
    assumptions: List[str] = Field(default_factory=list)
    days: List[DayPlan]

    def model_post_init(self, __context) -> None:
        if len(self.days) == 0:
            raise ValueError("days must not be empty")
