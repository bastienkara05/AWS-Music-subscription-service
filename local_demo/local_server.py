"""
Local demo backend — NO AWS REQUIRED.

Serves the same endpoints as the production Backend (app.py), but backed by
in-memory data instead of DynamoDB/S3. 

Run:
    pip install -r requirements.txt
    uvicorn local_server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import quote

app = FastAPI(title="Music Subscription Backend (Local Demo)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------

def image_for(artist: str) -> str:
    """Stand-in for the S3 artist image. Returns a labelled placeholder image."""
    return f"https://placehold.co/220x220/4f46e5/ffffff/png?text={quote(artist)}"


# Pre-seeded demo user so you can log in immediately: demo@example.com / demo123
USERS = {
    "demo@example.com": {
        "email": "demo@example.com",
        "user_name": "Demo User",
        "password": "demo123",
    }
}

# Sample catalogue
MUSIC = [
    {"artist": "Queen", "title": "Bohemian Rhapsody", "year": "1975", "album": "A Night at the Opera"},
    {"artist": "Queen", "title": "Don't Stop Me Now", "year": "1978", "album": "Jazz"},
    {"artist": "Fleetwood Mac", "title": "Dreams", "year": "1977", "album": "Rumours"},
    {"artist": "Fleetwood Mac", "title": "The Chain", "year": "1977", "album": "Rumours"},
    {"artist": "Daft Punk", "title": "Get Lucky", "year": "2013", "album": "Random Access Memories"},
    {"artist": "Daft Punk", "title": "Instant Crush", "year": "2013", "album": "Random Access Memories"},
    {"artist": "Tame Impala", "title": "The Less I Know The Better", "year": "2015", "album": "Currents"},
    {"artist": "Kendrick Lamar", "title": "HUMBLE.", "year": "2017", "album": "DAMN."},
    {"artist": "Dua Lipa", "title": "Levitating", "year": "2020", "album": "Future Nostalgia"},
    {"artist": "The Weeknd", "title": "Blinding Lights", "year": "2020", "album": "After Hours"},
]

for _song in MUSIC:
    _song["s3_image_url"] = image_for(_song["artist"])

# email -> list of subscribed songs
SUBSCRIPTIONS: dict[str, list[dict]] = {}


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Endpoints (mirror Backend/app.py)
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Music Subscription Backend (Local Demo) is running"}


@app.post("/login")
def login(request: LoginRequest):
    user = USERS.get(request.email.strip())
    if not user or user["password"] != request.password.strip():
        return {"success": False, "message": "email or password is invalid"}
    return {
        "success": True,
        "message": "login successful",
        "user": {"email": user["email"], "user_name": user["user_name"]},
    }


@app.post("/register")
def register(request: RegisterRequest):
    email = request.email.strip()
    if email in USERS:
        return {"success": False, "message": "The email already exists"}
    USERS[email] = {
        "email": email,
        "user_name": request.username.strip(),
        "password": request.password.strip(),
    }
    return {"success": True, "message": "registration successful"}


@app.get("/music/query")
def music_query(title: str = None, artist: str = None, year: str = None, album: str = None):
    if not any([title, artist, year, album]):
        return {"success": False, "message": "At least one field must be completed", "items": []}

    def matches(song):
        if title and title.strip().lower() not in song["title"].lower():
            return False
        if artist and artist.strip().lower() not in song["artist"].lower():
            return False
        if album and album.strip().lower() not in song["album"].lower():
            return False
        if year and year.strip() != song["year"]:
            return False
        return True

    items = [s for s in MUSIC if matches(s)]
    if not items:
        return {"success": False, "message": "No result is retrieved. Please query again", "items": []}
    return {"success": True, "message": "query successful", "items": items}


@app.get("/subscriptions/{email}")
def get_subscriptions(email: str):
    return {"success": True, "items": SUBSCRIPTIONS.get(email.strip(), [])}


@app.post("/subscriptions")
def add_subscription(request: SubscribeRequest):
    email = request.email.strip()
    song = dict(request.song)
    song.setdefault("s3_image_url", image_for(song.get("artist", "")))
    bucket = SUBSCRIPTIONS.setdefault(email, [])
    key = f"{song.get('artist')}#{song.get('title')}#{song.get('year')}"
    # avoid duplicates
    bucket[:] = [s for s in bucket if f"{s.get('artist')}#{s.get('title')}#{s.get('year')}" != key]
    bucket.append(song)
    return {"success": True, "message": "subscription added", "item": song}


@app.delete("/subscriptions/{email}/{artist_title_year}")
def remove_subscription(email: str, artist_title_year: str):
    email = email.strip()
    bucket = SUBSCRIPTIONS.get(email, [])
    bucket[:] = [
        s for s in bucket
        if f"{s.get('artist')}#{s.get('title')}#{s.get('year')}" != artist_title_year
    ]
    return {"success": True, "message": "subscription removed"}
