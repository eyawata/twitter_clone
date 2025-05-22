from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.tweets import router as tweets_router
from .routers.users import router as users_router

app = FastAPI(
    title="Twitter Clone",
)
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tweets_router, prefix="/tweets", tags=["tweets"])
