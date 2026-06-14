from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.task_log import TaskCategory


class TaskLogCreate(BaseModel):
    category: TaskCategory
    task_type: str


class TaskLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: TaskCategory
    task_type: str
    completed_at: datetime
    mood_delta: float


class CheckInRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_mood: int
    created_at: datetime


class StreakRead(BaseModel):
    current_streak: int
    longest_streak: int
