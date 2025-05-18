from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Tweet(BaseModel):
    username: str
    text: str


class Tweets(BaseModel):
    tweets: List[Tweet]


app = FastAPI()

# add any other origins to allow below
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_db = []


@app.get("/tweets", response_model=Tweets)
def get_tweets():
    return {"tweets": memory_db}


@app.post("/tweets")
def post_tweet(tweet: Tweet):
    memory_db.append(tweet)
    return {"message": "Tweet added successfully", "tweet": tweet}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
