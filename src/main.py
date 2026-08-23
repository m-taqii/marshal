from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from src.connectors.github.client import GithubClient
from src.connectors.discord.client import DiscordClient
from src.lib.db import init_db, close_db, SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.github = GithubClient()

    app.state.discord_bot = DiscordClient(github_client=app.state.github, db=SessionLocal)
    
    app.state.discord_task = asyncio.create_task(app.state.discord_bot.start())
    
    await init_db()
    
    yield
    
    # Shutdown
    await close_db()
    await app.state.discord_bot.stop()
    if getattr(app.state, "discord_task", None):
        app.state.discord_task.cancel()
    await app.state.github.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "System Running Perfectly"
    }