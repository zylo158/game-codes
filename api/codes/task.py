from __future__ import annotations

from loguru import logger
from api.constants import CodeStatus

from api.core.registry import get_integration, list_games
from api.core.scraper import scrape_game_codes
from api.db import db


async def update_codes() -> None:
    for game in list_games():
        integration = get_integration(game)
        if not integration:
            continue
        raw_codes = await scrape_game_codes(game)
        scraped_set: set[str] = {e["code"].upper() for e in raw_codes}

        for entry in raw_codes:
            existing = await db.redeemcode.find_first(
                where={"code": entry["code"], "game": game}
            )
            if existing:
                if existing.status in (CodeStatus.NOT_OK, CodeStatus.UNVERIFIED):
                    new_status = await integration.check_code(entry["code"])
                    if new_status != existing.status:
                        await db.redeemcode.update(
                            where={"id": existing.id},
                            data={"status": new_status},
                        )
                        logger.info(
                            f"Reactivated {entry['code']} for {game}: "
                            f"{existing.status} -> {new_status}"
                        )
                if entry.get("rewards") and not existing.rewards:
                    await db.redeemcode.update(
                        where={"id": existing.id},
                        data={"rewards": entry["rewards"]},
                    )
                continue
            status = await integration.check_code(entry["code"])
            await db.redeemcode.create(data={
                "code": entry["code"],
                "game": game,
                "status": status,
                "rewards": entry.get("rewards", ""),
                "source": "scraper",
            })
            logger.info(f"Added code {entry['code']} for {game}")

        if not scraped_set:
            logger.warning(f"Empty scrape for {game}, skipping expiry")
            continue

        active = await db.redeemcode.find_many(
            where={"game": game, "status": {"in": [CodeStatus.OK, CodeStatus.UNVERIFIED]}}
        )
        for entry in active:
            if entry.code not in scraped_set and entry.source != "manual":
                await db.redeemcode.update(
                    where={"id": entry.id},
                    data={"status": CodeStatus.NOT_OK},
                )
                logger.info(
                    f"Expired {entry.code} for {game}: "
                    f"no longer found on any source"
                )


async def check_codes() -> None:
    codes = await db.redeemcode.find_many(
        where={"status": {"in": [CodeStatus.OK, CodeStatus.UNVERIFIED]}}
    )
    for code in codes:
        integration = get_integration(code.game)
        if not integration or not integration.has_web_redemption:
            if code.status == CodeStatus.UNVERIFIED:
                await db.redeemcode.update(
                    where={"id": code.id},
                    data={"status": CodeStatus.OK},
                )
            continue
        new_status = await integration.verify_code(code.code)
        if new_status != code.status:
            await db.redeemcode.update(
                where={"id": code.id},
                data={"status": new_status},
            )
            logger.info(
                f"Updated {code.code} for {code.game}: "
                f"{code.status} -> {new_status}"
            )
