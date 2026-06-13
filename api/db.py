from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import shutil
from pathlib import Path
from typing import Any

from loguru import logger

SEED_FILE = Path("data.json")
DATA_FILE = Path(os.getenv("DATA_FILE", "data.json"))
BACKUP_FILE = DATA_FILE.with_name(DATA_FILE.name + ".bak")
DB_FILE = Path(os.getenv("DB_FILE", "game-codes.db"))


class Record:
    def __init__(self, **kwargs: Any) -> None:
        self.id: int = kwargs.get("id", 0)
        self.code: str = kwargs.get("code", "")
        self.game: str = kwargs.get("game", "")
        self.status: str = kwargs.get("status", "UNVERIFIED")
        self.rewards: str = kwargs.get("rewards", "")
        self.source: str = kwargs.get("source", "")

    def dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "game": self.game,
            "status": self.status,
            "rewards": self.rewards,
            "source": self.source,
        }


class RedeemCodeStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._records: list[Record] = []
        self._next_id = 1

    async def connect(self) -> None:
        self._seed_from_repo()
        self._migrate_from_sqlite()
        self._restore_from_backup()
        if DATA_FILE.exists():
            raw = json.loads(DATA_FILE.read_text("utf-8"))
            self._records = [Record(**r) for r in raw]
            self._next_id = max((r.id for r in self._records), default=0) + 1

    async def disconnect(self) -> None:
        pass

    def _migrate_from_sqlite(self) -> None:
        if DATA_FILE.exists() or not DB_FILE.exists():
            return
        try:
            conn = sqlite3.connect(str(DB_FILE))
            cur = conn.cursor()
            cur.execute("SELECT id, code, status, game, rewards, source FROM RedeemCode")
            rows = cur.fetchall()
            conn.close()
            if not rows:
                return
            records = [
                {"id": r[0], "code": r[1], "status": r[2], "game": r[3], "rewards": r[4], "source": r[5]}
                for r in rows
            ]
            self._write_json(records)
            logger.info(f"Migrated {len(records)} records from {DB_FILE.name} to {DATA_FILE.name}")
        except Exception:
            pass

    def _seed_from_repo(self) -> None:
        if DATA_FILE.exists():
            return
        if SEED_FILE.exists() and SEED_FILE.resolve() != DATA_FILE.resolve():
            try:
                json.loads(SEED_FILE.read_text("utf-8"))
                DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SEED_FILE, DATA_FILE)
                logger.info(f"Seeded {DATA_FILE} from {SEED_FILE}")
            except Exception as e:
                logger.warning(f"Seed failed: {e}")

    def _restore_from_backup(self) -> None:
        if DATA_FILE.exists():
            return
        if BACKUP_FILE.exists():
            try:
                json.loads(BACKUP_FILE.read_text("utf-8"))
                shutil.copy2(BACKUP_FILE, DATA_FILE)
                logger.info(f"Restored data from backup {BACKUP_FILE.name}")
            except Exception:
                pass

    def _write_json(self, data: list[dict[str, Any]]) -> None:
        tmp = DATA_FILE.with_suffix(".json.tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        json.loads(tmp.read_text("utf-8"))
        if BACKUP_FILE.exists():
            BACKUP_FILE.unlink()
        if DATA_FILE.exists():
            DATA_FILE.rename(BACKUP_FILE)
        tmp.rename(DATA_FILE)
        if BACKUP_FILE.exists():
            BACKUP_FILE.unlink()

    def _save(self) -> None:
        self._write_json([r.dict() for r in self._records])

    def _matches(self, record: Record, where: dict[str, Any]) -> bool:
        for key, value in where.items():
            if isinstance(value, dict) and "in" in value:
                if getattr(record, key, None) not in value["in"]:
                    return False
            elif getattr(record, key, None) != value:
                return False
        return True

    async def find_many(
        self, where: dict[str, Any] | None = None, order: dict[str, Any] | None = None
    ) -> list[Record]:
        async with self._lock:
            result = self._records[:]
            if where:
                result = [r for r in result if self._matches(r, where)]
            if order:
                for field, direction in order.items():
                    reverse = direction == "desc"
                    result.sort(key=lambda r, f=field: getattr(r, f, 0), reverse=reverse)
            return result

    async def find_first(self, where: dict[str, Any] | None = None) -> Record | None:
        result = await self.find_many(where=where)
        return result[0] if result else None

    async def create(self, data: dict[str, Any]) -> Record:
        async with self._lock:
            record = Record(**data)
            record.id = self._next_id
            self._next_id += 1
            self._records.append(record)
            self._save()
            return record

    async def update(self, where: dict[str, Any], data: dict[str, Any]) -> Record | None:
        async with self._lock:
            for record in self._records:
                if self._matches(record, where):
                    for key, value in data.items():
                        setattr(record, key, value)
                    self._save()
                    return record
            return None

    async def delete(self, where: dict[str, Any]) -> None:
        async with self._lock:
            self._records = [r for r in self._records if not self._matches(r, where)]
            self._save()


class _ModelProxy:
    def __init__(self, store: RedeemCodeStore) -> None:
        self._store = store

    async def find_many(self, where: dict[str, Any] | None = None, order: dict[str, Any] | None = None) -> list[Record]:
        return await self._store.find_many(where=where, order=order)

    async def find_first(self, where: dict[str, Any] | None = None) -> Record | None:
        return await self._store.find_first(where=where)

    async def create(self, data: dict[str, Any]) -> Record:
        return await self._store.create(data=data)

    async def update(self, where: dict[str, Any], data: dict[str, Any]) -> Record | None:
        return await self._store.update(where=where, data=data)

    async def delete(self, where: dict[str, Any]) -> None:
        return await self._store.delete(where=where)


class _DB:
    def __init__(self) -> None:
        self._store = RedeemCodeStore()

    @property
    def redeemcode(self) -> _ModelProxy:
        return _ModelProxy(self._store)

    async def connect(self) -> None:
        await self._store.connect()

    async def disconnect(self) -> None:
        await self._store.disconnect()


db: _DB = _DB()
