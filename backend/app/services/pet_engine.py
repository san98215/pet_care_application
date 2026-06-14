from dataclasses import dataclass

from app.models.task_log import TaskCategory
from app.schemas.user import PriorityWeight

# Mental health is always weighted as the primary category, regardless of
# the user's configured auxiliary priorities.
MENTAL_BASE_WEIGHT = 1.0
DEFAULT_AUX_WEIGHT = 0.3

BASE_MOOD_DELTA = 0.05
BASE_VITALITY_DELTA = 0.03


@dataclass
class StateDelta:
    mood_delta: float
    vitality_delta: float


class PetEngine:
    """Stub engine translating logged tasks into pet state changes.

    TODO: Streaks, time-of-day, and decay
    """

    def _weight_for_category(self, category: TaskCategory, priorities: list[PriorityWeight]) -> float:
        if category == TaskCategory.mental:
            return MENTAL_BASE_WEIGHT

        for priority in priorities:
            if priority.category == category.value:
                return priority.weight

        return DEFAULT_AUX_WEIGHT

    def compute_state_delta(
        self,
        category: TaskCategory,
        task_type: str,
        priorities: list[PriorityWeight],
    ) -> StateDelta:
        weight = self._weight_for_category(category, priorities)

        return StateDelta(
            mood_delta=round(BASE_MOOD_DELTA * weight, 4),
            vitality_delta=round(BASE_VITALITY_DELTA * weight, 4),
        )
