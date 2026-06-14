from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.database import get_db
from app.models.pet import Pet, PetState
from app.models.user import User
from app.schemas.pet import (
    CheckInCreate,
    PetCreate,
    PetHistoryEntry,
    PetRead,
    PetUpdate,
)
from app.schemas.task_log import CheckInRead

router = APIRouter(prefix="/pet", tags=["pet"])


async def _get_owned_pet(current_user: User, db: AsyncSession) -> Pet:
    pet = await db.scalar(
        select(Pet)
        .where(Pet.owner_id == current_user.id)
        .order_by(Pet.id)
        .options(selectinload(Pet.state))
    )
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pet found for this user")
    return pet


@router.get("", response_model=PetRead)
async def get_pet(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _get_owned_pet(current_user, db)


@router.post("", response_model=PetRead, status_code=status.HTTP_201_CREATED)
async def create_pet(
    payload: PetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pet = Pet(species=payload.species, name=payload.name, color=payload.color, owner_id=current_user.id)
    pet.state = PetState(mood=0.5, vitality=0.5, rolling_score_7d=0.5)
    db.add(pet)
    await db.commit()
    await db.refresh(pet, attribute_names=["state"])
    return pet


@router.patch("", response_model=PetRead)
async def update_pet(
    payload: PetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pet = await _get_owned_pet(current_user, db)
    if payload.name is not None:
        pet.name = payload.name
    if payload.color is not None:
        pet.color = payload.color
    await db.commit()
    return pet


@router.get("/history", response_model=list[PetHistoryEntry])
async def get_pet_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _get_owned_pet(current_user, db)
    return []


@router.post("/checkin", response_model=CheckInRead, status_code=status.HTTP_201_CREATED)
async def pet_checkin(
    payload: CheckInCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.task_log import CheckIn

    check_in = CheckIn(user_id=current_user.id, user_mood=payload.user_mood)
    db.add(check_in)
    await db.commit()
    await db.refresh(check_in)
    return check_in
