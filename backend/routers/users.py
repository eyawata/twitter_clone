import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from ..database import get_table

router = APIRouter()
USERS_TABLE = os.getenv("USERS_TABLE", "Users")
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# TODO refactor models later
# validate incoming data in request body when client creates or updates a user
class UserIn(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    bio: str | None


# determines what the API returns to client when user info requested
class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    profile_picture: str | None
    bio: str | None


def users_table_dep():
    return get_table(USERS_TABLE)


# === GET a user with user_id ===
@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: str, users_tbl=Depends(users_table_dep)):
    """
    - Fetches a user by PK
    """
    response = users_tbl.get_item(Key={"user_id": user_id})
    if "Item" not in response:
        raise HTTPException(404, "User not found")

    item = response["Item"]
    return UserOut(
        id=item["user_id"],
        username=item["username"],
        email=item["email"],
        profile_picture=item.get("profile_picture", None),
        bio=item.get("bio", None),
    )


# === GET akk user ===
@router.get("/", response_model=list[UserOut])
def list_users(users_tbl=Depends(users_table_dep)):
    """
    - Fetches all users
    """
    response = users_tbl.scan()
    items = response.get("Items", [])

    return [
        UserOut(
            id=item["user_id"],
            username=item["username"],
            email=item["email"],
            profile_picture=item.get("profile_picture", None),
            bio=item.get("bio", None),
        )
        for item in items
    ]


# === CREATE a user ===
@router.post("/", response_model=UserOut, status_code=201)
def create_user(body: UserIn, users_tbl=Depends(users_table_dep)):
    """
    - Hashes the password
    - Fails if email already exists
    """

    user_id = str(uuid.uuid4())
    pwd_hash = pwd_ctx.hash(body.password)
    item = {
        "user_id": user_id,
        "username": body.username,
        "email": body.email,
        "password_hash": pwd_hash,
        "profile_picture": None,
        "bio": body.bio or "",
    }

    try:
        users_tbl.put_item(Item=item, ConditionExpression="attribute_not_exists(email)")
    except Exception:
        raise HTTPException(400, f"Could not create user: {Exception}")

    return UserOut(
        id=item["user_id"],
        username=item["username"],
        email=item["email"],
        profile_picture=item["profile_picture"],
        bio=item["bio"],
    )
