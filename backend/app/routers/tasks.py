from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.task_log import TaskLog
from app.models.user import User
from app.schemas.task_log import TaskLogCreate, TaskLogRead
from app.schemas.user import PriorityWeight
from app.services.pet_engine import PetEngine

router = APIRouter(tags=["tasks"])

pet_engine = PetEngine()

# small set of tasks used as a placeholder for now
AVAILABLE_TASKS = {
    "mental": ["meditation", "journaling", "therapy_session"],
    "physical": ["walk", "workout", "stretching"],
    "sleep": ["early_bedtime", "nap", "wind_down_routine"],
    "nutrition": ["balanced_meal", "hydration", "meal_prep"],
    "social": ["call_a_friend", "group_activity", "quality_time"],
}


@router.get("/tasks")
async def list_tasks():
    return AVAILABLE_TASKS


@router.post("/tasks/log", response_model=TaskLogRead, status_code=status.HTTP_201_CREATED)
async def log_task(
    payload: TaskLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    priorities = [PriorityWeight(**p) for p in current_user.priorities]
    delta = pet_engine.compute_state_delta(payload.category, payload.task_type, priorities)

    task_log = TaskLog(
        user_id=current_user.id,
        category=payload.category,
        task_type=payload.task_type,
        mood_delta=delta.mood_delta,
    )
    db.add(task_log)
    await db.commit()
    await db.refresh(task_log)
    return task_log


@router.get("/tasks/log", response_model=list[TaskLogRead])
async def get_task_logs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(TaskLog).where(TaskLog.user_id == current_user.id).order_by(TaskLog.completed_at.desc())
    )
    return result.all()


@router.get("/tasks/log/today", response_model=list[TaskLogRead])
async def get_todays_task_logs(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    result = await db.scalars(
        select(TaskLog)
        .where(TaskLog.user_id == current_user.id, TaskLog.completed_at >= today_start)
        .order_by(TaskLog.completed_at.desc())
    )
    return result.all()


@router.delete("/tasks/log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task_log = await db.get(TaskLog, log_id)
    if task_log is None or task_log.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task log not found")

    await db.delete(task_log)
    await db.commit()
    return None
