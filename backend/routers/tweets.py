import os
import uuid
from datetime import datetime, timezone
from typing import List

from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..database import get_table
from .auth import get_current_user

router = APIRouter()
TWEETS_TABLE = os.getenv("TWEETS_TABLE", "Tweets")
USERS_TABLE = os.getenv("USERS_TABLE", "Users")


# TODO refactor schema later
# ───── Schema ─────
class TweetIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=280)


class TweetOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    username: str
    text: str
    created_at: datetime


def tweets_table_dep():
    return get_table(TWEETS_TABLE)


# ───── Create a Tweet with current user (protected) ─────
@router.post(
    "/",
    response_model=TweetOut,
    status_code=201,
    dependencies=[Depends(get_current_user)],
)
def create_tweet(
    body: TweetIn,
    tweets_tbl=Depends(tweets_table_dep),
    current_user: dict = Depends(get_current_user),
):
    """
    - Creates a new tweet
    """
    tweet_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    item = {
        "tweet_id": tweet_id,
        "created_at": created_at,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "text": body.text,
    }

    try:
        tweets_tbl.put_item(Item=item)
    except Exception as e:
        raise HTTPException(400, f"Could not create tweet: {e}")

    return TweetOut(
        id=uuid.UUID(item["tweet_id"]),
        user_id=uuid.UUID(item["user_id"]),
        username=item["username"],
        text=item["text"],
        created_at=datetime.fromisoformat(item["created_at"]),
    )


# ───── Lists all tweets by user (unprotected) ─────
@router.get(
    "/{username}/timelines/tweets",
    response_model=List[TweetOut],
)
def list_tweets_by_user(
    username: str,
    tweets_tbl=Depends(tweets_table_dep),
):
    """
    Returns the user's tweets by username, sorted by newest first
    """
    response = tweets_tbl.query(
        IndexName="ByUsername",
        KeyConditionExpression=Key("username").eq(username),
        ScanIndexForward=False,
    )
    items = response.get("Items", [])

    return [
        TweetOut(
            id=uuid.UUID(item["tweet_id"]),
            user_id=uuid.UUID(item["user_id"]),
            username=item["username"],
            text=item["text"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in items
    ]


# ───── Get a tweet (unprotected) ─────
@router.get("/{tweet_id}", response_model=TweetOut)
def read_tweet(
    tweet_id: str,
    created_at: str,
    tweets_tbl=Depends(tweets_table_dep),
):
    """
    - Fetches a tweet by its composite key (id + created_at)
    """
    response = tweets_tbl.get_item(Key={"tweet_id": tweet_id, "created_at": created_at})
    if "Item" not in response:
        raise HTTPException(404, "Tweet not found")

    item = response["Item"]
    return TweetOut(
        id=uuid.UUID(item["tweet_id"]),
        user_id=uuid.UUID(item["user_id"]),
        username=item["username"],
        text=item["text"],
        created_at=datetime.fromisoformat(item["created_at"]),
    )


# ───── Lists all tweets (unprotected) ─────
@router.get("/", response_model=List[TweetOut])
def list_tweets(tweets_tbl=Depends(tweets_table_dep)):
    """
    - Scans and returns *all* tweets
    """
    response = tweets_tbl.scan()
    items = response.get("Items", [])

    return [
        TweetOut(
            id=uuid.UUID(item["tweet_id"]),
            user_id=uuid.UUID(item["user_id"]),
            username=item["username"],
            text=item["text"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in items
    ]


# ───── Lists all tweets by current user (protected) ─────
@router.get(
    "/me",
    response_model=List[TweetOut],
    dependencies=[Depends(get_current_user)],
)
def list_my_tweets(
    tweets_tbl=Depends(tweets_table_dep),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns the authenticated user’s tweets, newest first.
    """
    response = tweets_tbl.query(
        IndexName="ByUser",
        KeyConditionExpression=Key("user_id").eq(current_user["user_id"]),
        ScanIndexForward=False,
    )
    items = response.get("Items", [])

    return [
        TweetOut(
            id=uuid.UUID(item["tweet_id"]),
            user_id=uuid.UUID(item["user_id"]),
            username=item["username"],
            text=item["text"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in items
    ]
