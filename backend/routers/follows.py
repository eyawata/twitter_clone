# # routers/follows.py
# import os
# import uuid

# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, EmailStr, Field

# from ..database import get_table
# from .auth import get_current_user

# router = APIRouter()
# USERS_TABLE = os.getenv("USERS_TABLE", "Users")

# class FollowIn(BaseModel):
#     id: uuid.UUID
#     follower_username: str
#     following_username: str

# class FollowOut(BaseModel):
#     id: uuid.UUID
#     follower_username: str
#     following_username: str


# def users_table_dep():
#     return get_table(USERS_TABLE)

# # ───── Create a follow (protected) ─────
# @router.post("/follow")
# def follow_user(body: FollowIn)
