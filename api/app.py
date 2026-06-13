from __future__ import annotations

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from api.config import settings
from api.constants import CodeStatus, Game, GAME_DESCRIPTIONS, GAME_NAMES
from api.codes.task import check_codes, update_codes
from api.db import db
from api.models import CreateCode
from api.ratelimit import RateLimitMiddleware

security = HTTPBearer(auto_error=False)
scheduler = AsyncIOScheduler()


def verify_token(credentials: HTTPAuthorizationCredentials | None = Security(security)):
    if not settings.api_token:
        return True
    if not credentials or credentials.credentials != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    scheduler.add_job(update_codes, "interval", hours=1, id="update")
    scheduler.add_job(
        check_codes, "cron", hour=1, minute=30, timezone="Asia/Taipei", id="check"
    )
    scheduler.start()
    logger.info("Started scheduler")
    yield
    scheduler.shutdown()


app = FastAPI(title="Game Codes API", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware, max_requests=30, window=60)


@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/games")
async def list_games():
    return {
        slug: {"name": GAME_NAMES.get(slug, ""), "description": GAME_DESCRIPTIONS.get(slug, "")}
        for slug in Game.values()
    }


@app.get("/codes")
async def get_codes(game: str):
    if game not in Game.values():
        raise HTTPException(
            status_code=404,
            detail=f"Unknown game: {game}. Must be one of {Game.values()}",
        )
    codes = await db.redeemcode.find_many(
        where={"game": game, "status": CodeStatus.OK},
        order={"id": "desc"},
    )
    unverified = await db.redeemcode.find_many(
        where={"game": game, "status": CodeStatus.UNVERIFIED},
        order={"id": "desc"},
    )
    return {
        "game": game,
        "codes": [
            {"id": c.id, "code": c.code, "rewards": c.rewards, "source": c.source}
            for c in codes
        ],
        "unverified": [
            {"id": c.id, "code": c.code, "rewards": c.rewards, "source": c.source}
            for c in unverified
        ],
    }


@app.post("/codes")
async def add_code(data: CreateCode, _=Depends(verify_token)):
    existing = await db.redeemcode.find_first(
        where={"code": data.code, "game": data.game}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Code already exists")
    created = await db.redeemcode.create(data={
        "code": data.code,
        "game": data.game,
        "status": CodeStatus.UNVERIFIED,
        "rewards": "",
        "source": "manual",
    })
    return {"id": created.id, "code": created.code}


@app.delete("/codes/{code_id}")
async def delete_code(code_id: int, _=Depends(verify_token)):
    await db.redeemcode.delete(where={"id": code_id})
    return {"ok": True}


@app.post("/update-codes")
async def trigger_update(_=Depends(verify_token)):
    await update_codes()
    return {"ok": True}


@app.post("/check-codes")
async def trigger_check(_=Depends(verify_token)):
    await check_codes()
    return {"ok": True}
