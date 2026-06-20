


https://github.com/user-attachments/assets/fa0ca704-587e-496d-9681-52e4cf12e3d8




# Music Subscription Service

A full-stack cloud application that lets users register, search a music catalogue, and manage their own subscription list. Built on AWS with a React frontend, a Python API, and DynamoDB for storage. The backend is implemented to run in **three interchangeable deployment modes** — EC2, ECS Fargate (containerised), and AWS Lambda behind API Gateway — to demonstrate different cloud compute models.

## Features

- **User authentication** — register and log in with email/password.
- **Music search** — query a catalogue by title, artist, year, and/or album, with results enriched by artist images served from S3.
- **Subscriptions** — add songs to a personal list, view it, and remove items.
- **Multiple deployment targets** — the same API logic runs on EC2, ECS Fargate, and Lambda, showcasing trade-offs between each.

## Architecture

```
        ┌──────────────┐
        │ React (Vite) │   Login + MainPage, React Router
        │   frontend   │
        └──────┬───────┘
               │ HTTPS / REST
     ┌─────────┼──────────┐
     ▼         ▼          ▼
  ┌──────┐ ┌───────┐ ┌──────────────────┐
  │ EC2  │ │  ECS  │ │ Lambda +         │
  │FastAPI│ │Fargate│ │ API Gateway      │   compute layer (3 options)
  └──┬───┘ └───┬───┘ └────────┬─────────┘
     └─────────┼──────────────┘
               ▼
       ┌───────────────┐      ┌──────────────┐
       │   DynamoDB    │      │      S3      │
       │ login / music │      │ artist images│
       │ subscriptions │      └──────────────┘
       └───────────────┘
```

## Tech Stack

| Layer        | Technology                                              |
|--------------|---------------------------------------------------------|
| Frontend     | React 19, Vite, React Router                            |
| Backend      | Python, FastAPI (EC2/ECS), AWS Lambda                   |
| Database     | Amazon DynamoDB (with LSI and GSI for query patterns)   |
| Storage      | Amazon S3 (artist images)                               |
| Deployment   | Docker, Amazon ECR, ECS Fargate, API Gateway            |

## Data Model

Three DynamoDB tables (see `Database/create_tables.py`):

- **`login`** — partition key `email`. Stores user credentials and username.
- **`music`** — partition key `artist`, sort key `title_year`.
  - `LSI_Year` — local secondary index on `artist` + `year`.
  - `GSI_Title` — global secondary index on `title` + `artist`.
- **`subscriptions`** — partition key `email`, sort key `artist_title_year`.

The indexes let the API serve common lookups (by title, or by artist + year) as efficient queries instead of full table scans.

## Project Structure

```
.
├── Backend/                # API logic
│   ├── app.py              # FastAPI app (EC2 / ECS)
│   ├── lambda_function.py  # AWS Lambda handler
│   ├── db_operations.py    # DynamoDB + S3 access layer
│   ├── Docker File.txt     # Container image definition
│   ├── task-definition.json# ECS Fargate task definition
│   └── requirements.txt
├── Database/               # One-off setup / seed scripts
│   ├── create_tables.py    # Creates DynamoDB tables + indexes
│   ├── load_music.py       # Loads the music catalogue
│   ├── upload_images.py    # Uploads artist images to S3
│   └── seed_login.py       # Seeds sample users
└── frontend2/my-react-app/ # React + Vite frontend
    └── src/                # Login.jsx, MainPage.jsx, api.js
```

## API Endpoints

| Method | Path                                        | Description                  |
|--------|---------------------------------------------|------------------------------|
| GET    | `/`                                         | Health check                 |
| POST   | `/login`                                    | Authenticate a user          |
| POST   | `/register`                                 | Create a user                |
| GET    | `/music/query?title=&artist=&year=&album=`  | Search the catalogue         |
| GET    | `/subscriptions/{email}`                    | List a user's subscriptions  |
| POST   | `/subscriptions`                            | Add a subscription           |
| DELETE | `/subscriptions/{email}/{artist_title_year}`| Remove a subscription        |

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- An AWS account with credentials configured (`aws configure`)

### 1. Provision AWS resources

```bash
cd Database
pip install boto3
python create_tables.py      # create DynamoDB tables + indexes
python load_music.py         # load the catalogue
python upload_images.py      # upload artist images to S3
python seed_login.py         # (optional) seed sample users
```

### 2. Run the backend locally

```bash
cd Backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# API available at http://localhost:8000
```

### 3. Run the frontend

```bash
cd frontend2/my-react-app
npm install
npm run dev
# App available at http://localhost:5173
```

Update the endpoint URLs in `frontend2/my-react-app/src/api.js` to point at your backend (local or deployed).

## Deployment

**ECS Fargate (containerised):**

```bash
cd Backend
docker build -t music-backend .
# Tag and push to Amazon ECR, then deploy with task-definition.json
```

**Lambda:** package `lambda_function.py` and deploy behind API Gateway.

> Note: `task-definition.json` uses placeholder account IDs and role ARNs — replace `<AWS_ACCOUNT_ID>` and `<EXECUTION_ROLE>` with your own before deploying.

## Roadmap / Known Limitations

This started as a cloud-computing coursework project. Items I'd address to make it production-grade:

- **Password hashing** — credentials are currently stored in plaintext; should use `bcrypt`/`argon2`.
- **Tighten CORS** — replace `allow_origins=["*"]` with an allow-list.
- **JWT-based sessions** instead of `sessionStorage` user state.
- **Input validation and rate limiting** on auth endpoints.

## License

MIT
