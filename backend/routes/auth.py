from fastapi import APIRouter, status, Depends

from backend.core.db import AsyncSessionDep
from backend.core.deps import get_current_user
from backend.models import Iam
from backend.schemas.auth import TokenResponse, LoginRequest, RefreshResponse, RefreshRequest, MessageResponse
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: AsyncSessionDep):
    """Authenticate user and return JWT tokens"""
    return await auth_service.login(db, payload.email, payload.password)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSessionDep):
    """Exchange valid refresh token for new access token"""
    return await auth_service.refresh_access_token(db, payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    db: AsyncSessionDep,
    current_user: Iam = Depends(get_current_user)  # From your dependencies.py
):
    """Invalidate tokens and clear refresh token"""
    return await auth_service.logout(db, current_user.iam_id)

# @router.post("/toggle-role", response_model=TokenResponse)
# async def toggle_ac_role(
#     db: AsyncSessionDep,
#     current_user: Iam = Depends(get_current_user)
# ):
#     """Toggle Academic Coordinator between AC/LECTURER roles"""
#     return await auth_service.toggle_ac_role(db, current_user.iam_id)