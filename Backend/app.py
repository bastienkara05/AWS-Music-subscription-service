from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db_operations import (
    login_user,
    register_user,
    query_music,
    get_subscriptions,
    add_subscription,
    remove_subscription
)

app = FastAPI(title="Music Subscription Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class SubscribeRequest(BaseModel):
    email: str
    song: dict


@app.get("/")
def root():
    return {"message": "Music Subscription Backend is running"}


@app.post("/login")
def login(request: LoginRequest):
    return login_user(request.email, request.password)


@app.post("/register")
def register(request: RegisterRequest):
    return register_user(request.email, request.username, request.password)


@app.get("/music/query")
def music_query(
    title: str = None,
    artist: str = None,
    year: str = None,
    album: str = None
):
    return query_music(title=title, artist=artist, year=year, album=album)


@app.get("/subscriptions/{email}")
def subscriptions(email: str):
    return get_subscriptions(email)


@app.post("/subscriptions")
def subscribe(request: SubscribeRequest):
    return add_subscription(request.email, request.song)


@app.delete("/subscriptions/{email}/{artist_title_year}")
def delete_subscription(email: str, artist_title_year: str):
    return remove_subscription(email, artist_title_year)