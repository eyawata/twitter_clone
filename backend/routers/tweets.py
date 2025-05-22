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
        "text": body.text,
    }

    try:
        tweets_tbl.put_item(Item=item)
    except Exception as e:
        raise HTTPException(400, f"Could not create tweet: {e}")

    return TweetOut(
        id=uuid.UUID(item["tweet_id"]),
        user_id=uuid.UUID(item["user_id"]),
        text=item["text"],
        created_at=datetime.fromisoformat(item["created_at"]),
    )

    # ───── Get all tweets by a user (unprotected) ─────
    # @router.get("/by-user/{username}", response_model=List[TweetOut])
    # def list_tweets_by_user(
    #     username: str,
    #     tweets_tbl=Depends(tweets_table_dep),
    #     users_tbl=Depends(users_table_dep),
    # ):
    #     """
    #     - Queries tweets for a given user (uses the `ByUser` GSI), newest first
    #     """
    #     users_resp = users_tbl.scan()
    #     if "Item" not in resp:
    #         raise HTTPException(404, "User not found")

    #     it = resp["Item"]

    #     tweets_resp = tweets_tbl.query(
    #         IndexName="ByUser",
    #         KeyConditionExpression=Key("user_id").eq(user_id),
    #         ScanIndexForward=False,  # descending by created_at
    #     )
    #     items = tweets_resp.get("Items", [])
    # return [
    #     TweetOut(
    #         id=uuid.UUID(item["tweet_id"]),
    #         user_id=uuid.UUID(item["user_id"]),
    #         text=item["text"],
    #         created_at=datetime.fromisoformat(item["created_at"]),
    #     )
    #     for item in items """
    # ]


# ───── Get a tweet (unprotected) ─────
@router.get("/{tweet_id}/{created_at}", response_model=TweetOut)
def read_tweet(
    tweet_id: str,
    created_at: str,
    tweets_tbl=Depends(tweets_table_dep),
):
    """
    - Fetches a tweet by its composite key (id + created_at)
    """
    resp = tweets_tbl.get_item(Key={"tweet_id": tweet_id, "created_at": created_at})
    if "Item" not in resp:
        raise HTTPException(404, "Tweet not found")

    it = resp["Item"]
    return TweetOut(
        id=uuid.UUID(it["tweet_id"]),
        user_id=uuid.UUID(it["user_id"]),
        text=it["text"],
        created_at=datetime.fromisoformat(it["created_at"]),
    )


# ───── Lists all tweets (unprotected) ─────
@router.get("/", response_model=List[TweetOut])
def list_tweets(tweets_tbl=Depends(tweets_table_dep)):
    """
    - Scans and returns *all* tweets
    """
    resp = tweets_tbl.scan()
    items = resp.get("Items", [])

    return [
        TweetOut(
            id=uuid.UUID(item["tweet_id"]),
            user_id=uuid.UUID(item["user_id"]),
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
    resp = tweets_tbl.query(
        IndexName="ByUser",
        KeyConditionExpression=Key("user_id").eq(current_user["user_id"]),
        ScanIndexForward=False,
    )
    items = resp.get("Items", [])

    return [
        TweetOut(
            id=uuid.UUID(item["tweet_id"]),
            user_id=uuid.UUID(item["user_id"]),
            text=item["text"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in items
    ]
