from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.database import get_db
from app.models.pet import Pet
from app.models.task_log import TaskLog
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total_logs = await db.scalar(
        select(func.count()).select_from(TaskLog).where(TaskLog.user_id == current_user.id)
    )
    return {
        "total_tasks_logged": total_logs or 0,
        "categories": [],
        "pet": None,
    }


@router.get("/categories")
async def get_category_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = await db.execute(
        select(TaskLog.category, func.count(), func.avg(TaskLog.mood_delta))
        .where(TaskLog.user_id == current_user.id)
        .group_by(TaskLog.category)
    )
    return [
        {"category": category.value, "count": count, "avg_mood_delta": float(avg_delta or 0.0)}
        for category, count, avg_delta in rows.all()
    ]


@router.get("/pet")
async def get_pet_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pet = await db.scalar(
        select(Pet)
        .where(Pet.owner_id == current_user.id)
        .order_by(Pet.id)
        .options(selectinload(Pet.state))
    )
    if pet is None or pet.state is None:
        return {"mood": None, "vitality": None, "rolling_score_7d": None}

    return {
        "mood": pet.state.mood,
        "vitality": pet.state.vitality,
        "rolling_score_7d": pet.state.rolling_score_7d,
    }
