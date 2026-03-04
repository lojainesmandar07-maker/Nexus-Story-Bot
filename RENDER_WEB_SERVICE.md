# Render Web Service Setup (Free) for Nexus Story Bot

Use this when creating a **Web Service** on Render.

## Service settings
- **Language**: Python 3
- **Branch**: `main`
- **Root Directory**: *(leave empty)*
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

> ⚠️ Important: do **not** use `main.py` alone as Start Command.
> It must be `python main.py` (or `python3 main.py`).

## Environment Variables
Add these in Render > Environment:

- `TOKEN` = your Discord bot token (required)
- `ENVIRONMENT` = `production` (optional)

## Important notes
- This project starts a Flask keep-alive endpoint from `main.py`.
- `web/server.py` reads Render's `PORT` env var automatically (fallback: `8080`).
- If `TOKEN` is missing, app will exit immediately by design.

## Health check URLs (after deploy)
- `/`
- `/health`
- `/stats`

Example:
`https://your-render-service.onrender.com/health`


## Optional (recommended): Blueprint deploy
This repo now includes `render.yaml` so you can deploy with Render Blueprint and avoid command typos.
