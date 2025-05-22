# routers/users.py
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from ..database import get_table
from .auth import get_current_user

router = APIRouter()
USERS_TABLE = os.getenv("USERS_TABLE", "Users")


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    profile_picture: str | None
    bio: str | None


def users_table_dep():
    return get_table(USERS_TABLE)


# ───── List all users (public) ─────
@router.get("/", response_model=list[UserOut])
def list_users(users_tbl=Depends(users_table_dep)):
    resp = users_tbl.scan()
    items = resp.get("Items", [])
    return [
        UserOut(
            id=item["user_id"],
            username=item["username"],
            email=item["email"],
            profile_picture=item.get("profile_picture"),
            bio=item.get("bio"),
        )
        for item in items
    ]


# ───── Get *your* profile (requires JWT) ─────
@router.get("/me", response_model=UserOut)
def read_me(current_user: dict = Depends(get_current_user)):
    return UserOut(
        id=current_user["user_id"],
        username=current_user["username"],
        email=current_user["email"],
        profile_picture=current_user.get("profile_picture"),
        bio=current_user.get("bio"),
    )
