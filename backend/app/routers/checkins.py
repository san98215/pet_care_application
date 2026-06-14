from datetime import timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.task_log import CheckIn
from app.models.user import User
from app.schemas.pet import CheckInCreate
from app.schemas.task_log import CheckInRead, StreakRead

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("", response_model=CheckInRead, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    payload: CheckInCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_in = CheckIn(user_id=current_user.id, user_mood=payload.user_mood)
    db.add(check_in)
    await db.commit()
    await db.refresh(check_in)
    return check_in


@router.get("", response_model=list[CheckInRead])
async def list_checkins(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(CheckIn).where(CheckIn.user_id == current_user.id).order_by(CheckIn.created_at.desc())
    )
    return result.all()


@router.get("/streak", response_model=StreakRead)
async def get_streak(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(CheckIn).where(CheckIn.user_id == current_user.id).order_by(CheckIn.created_at.desc())
    )
    check_ins = result.all()
    if not check_ins:
        return StreakRead(current_streak=0, longest_streak=0)

    dates = sorted({c.created_at.date() for c in check_ins}, reverse=True)

    current_streak = 0
    expected = dates[0]
    for d in dates:
        if d == expected:
            current_streak += 1
            expected = expected - timedelta(days=1)
        else:
            break

    longest_streak = 1
    run = 1
    for prev, curr in zip(dates, dates[1:]):
        if prev - curr == timedelta(days=1):
            run += 1
        else:
            longest_streak = max(longest_streak, run)
            run = 1
    longest_streak = max(longest_streak, run, current_streak)

    return StreakRead(current_streak=current_streak, longest_streak=longest_streak)
