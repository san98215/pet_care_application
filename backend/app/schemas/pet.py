from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PetCreate(BaseModel):
    species: str
    name: str
    color: str


class PetUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class PetStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mood: float
    vitality: float
    rolling_score_7d: float
    last_updated: datetime


class PetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    species: str
    name: str
    color: str
    # nests the related PetState row into the pet response
    state: PetStateRead | None = None


class PetHistoryEntry(BaseModel):
    recorded_at: datetime
    mood: float
    vitality: float


# user_mood is a 1-5 self-reported scale, shared by /pet/checkin and /checkins
class CheckInCreate(BaseModel):
    user_mood: int = Field(ge=1, le=5)
