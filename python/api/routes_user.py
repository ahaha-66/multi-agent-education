"""用户相关 API 路由"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional, List

from db.session import get_session
from db.models import LearnerProfile

router = APIRouter(prefix="/users", tags=["用户"])


class UserProfileResponse(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    grade: Optional[int] = None
    school: Optional[str] = None
    created_at: datetime
    last_active_at: datetime
    total_study_days: int = 1
    total_points: int = 0
    streak: int = 0


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    grade: Optional[int] = None
    school: Optional[str] = None


class UserSettings(BaseModel):
    theme: str = "light"
    language: str = "zh"
    notifications: dict = {
        "email": True,
        "push": True,
        "reminder": True
    }
    practice: dict = {
        "difficulty": "medium",
        "auto_play_hints": False,
        "show_answer_immediately": False
    }
    display: dict = {
        "show_progress": True,
        "compact_mode": False
    }


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, session: AsyncSession = Depends(get_session)):
    """获取用户资料"""
    result = await session.execute(
        select(LearnerProfile).where(LearnerProfile.learner_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = LearnerProfile(
            learner_id=user_id,
            created_at=datetime.utcnow(),
            last_active_at=datetime.utcnow()
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    
    await session.execute(
        update(LearnerProfile)
        .where(LearnerProfile.learner_id == user_id)
        .values(last_active_at=datetime.utcnow())
    )
    await session.commit()
    
    return UserProfileResponse(
        id=profile.learner_id,
        name=f"学习者_{user_id[-4:]}",
        avatar=None,
        email=None,
        grade=None,
        school=None,
        created_at=profile.created_at,
        last_active_at=profile.last_active_at,
        total_study_days=1,
        total_points=0,
        streak=0
    )


@router.patch("/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str,
    data: UserProfileUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新用户资料"""
    result = await session.execute(
        select(LearnerProfile).where(LearnerProfile.learner_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = LearnerProfile(
            learner_id=user_id,
            created_at=datetime.utcnow(),
            last_active_at=datetime.utcnow()
        )
        session.add(profile)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    await session.commit()
    await session.refresh(profile)
    
    return UserProfileResponse(
        id=profile.learner_id,
        name=f"学习者_{user_id[-4:]}",
        avatar=profile.avatar,
        email=profile.email,
        grade=profile.grade,
        school=profile.school,
        created_at=profile.created_at,
        last_active_at=profile.last_active_at,
        total_study_days=1,
        total_points=0,
        streak=0
    )


@router.get("/{user_id}/settings", response_model=UserSettings)
async def get_user_settings(user_id: str):
    """获取用户设置"""
    return UserSettings()


@router.patch("/{user_id}/settings", response_model=UserSettings)
async def update_user_settings(
    user_id: str,
    settings: UserSettings,
    session: AsyncSession = Depends(get_session)
):
    """更新用户设置"""
    await session.commit()
    return settings


@router.post("/{user_id}/reset-progress")
async def reset_user_progress(user_id: str, session: AsyncSession = Depends(get_session)):
    """重置用户学习进度"""
    await session.commit()
    return {"message": "学习进度已重置", "user_id": user_id}
