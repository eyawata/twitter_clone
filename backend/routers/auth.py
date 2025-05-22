# routers/auth.py
import datetime
import os
import uuid
from pathlib import Path

from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from ..database import get_table

# ─── Config ──────────────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()  # we’ll mount under /auth in main.py
USERS_TABLE = os.getenv("USERS_TABLE", "Users")


def users_table_dep():
    return get_table(USERS_TABLE)


# ─── Schemas ─────────────────────────────────────────────────
class SignupIn(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    bio: str | None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Helpers ────────────────────────────────────────────────
def create_access_token(subject: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─── Routes ─────────────────────────────────────────────────
@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(data: SignupIn, users_tbl=Depends(users_table_dep)):
    try:
        user_id = str(uuid.uuid4())
        pwd_hash = pwd_ctx.hash(data.password)
        item = {
            "user_id": user_id,
            "username": data.username,
            "email": data.email,
            "password_hash": pwd_hash,
            "bio": data.bio,
        }
        users_tbl.put_item(Item=item, ConditionExpression=Attr("email").not_exists())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not sign up: {e}")

    token = create_access_token(user_id)
    return {"access_token": token}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_tbl=Depends(users_table_dep),
):
    # lookup by email
    resp = users_tbl.scan(
        FilterExpression=Attr("username").eq(form_data.username), Limit=1
    )
    items = resp.get("Items", [])
    if not items or not pwd_ctx.verify(form_data.password, items[0]["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(items[0]["user_id"])
    return {"access_token": token}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    users_tbl=Depends(users_table_dep),
):
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise creds_exc
    except JWTError:
        raise creds_exc

    resp = users_tbl.get_item(Key={"user_id": user_id})
    if "Item" not in resp:
        raise creds_exc

    return resp["Item"]
