# Local Demo (no AWS required)

Run the whole app on your machine with zero cloud setup — ideal for recording a
demo GIF/video. This backend mirrors the production API (`Backend/app.py`) but
stores data in memory and uses placeholder artist images instead of DynamoDB/S3.

## Prerequisites

- Python 3.9+
- Node.js 18+ and npm

## 1. Start the local backend

```bash
cd local_demo
pip install -r requirements.txt
uvicorn local_server:app --reload --port 8000
```

Leave this running. The API is now at `http://localhost:8000`.

## 2. Start the frontend (in a second terminal)

```bash
cd frontend2/my-react-app
npm install
npm run dev
```

Open the URL it prints (usually `http://localhost:5173`).

> `src/api.js` already defaults all three endpoints (EC2 / Lambda / ECS) to
> `http://localhost:8000`, so no config changes are needed.

## 3. Log in

Use the pre-seeded account, or click **Signup** to create your own:

- **Email:** `demo@example.com`
- **Password:** `demo123`

## Suggested demo flow (for the recording)

1. Log in with the demo account.
2. In **Search Music**, type an artist (e.g. `Queen`, `Daft Punk`, `Dua Lipa`) and click **Query**.
3. Click **Subscribe** on a result.
4. Show it appear under **Your Subscriptions**.
5. Click **Remove** to show it disappear.

Sample data includes Queen, Fleetwood Mac, Daft Punk, Tame Impala, Kendrick
Lamar, Dua Lipa, and The Weeknd. Search is case-insensitive and matches partial
titles/artists/albums.

## Notes

- Data resets every time you restart the server (it's in memory by design).
- This folder is **only** for local demos. The real cloud code lives in
  `Backend/`, `Database/`, and is deployed via Docker/ECS/Lambda.
