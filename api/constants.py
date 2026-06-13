from __future__ import annotations

from typing import Final


class Game:
    wuwa: Final[str] = "wuwa"
    nte: Final[str] = "nte"
    bluearchive: Final[str] = "bluearchive"
    endfield: Final[str] = "endfield"

    _ALL: list[str] = ["wuwa", "nte", "bluearchive", "endfield"]

    @classmethod
    def values(cls) -> list[str]:
        return list(cls._ALL)


GAME_NAMES: Final[dict[str, str]] = {
    Game.wuwa: "Wuthering Waves",
    Game.nte: "Neverness to Everness",
    Game.bluearchive: "Blue Archive",
    Game.endfield: "Arknights: Endfield",
}

GAME_DESCRIPTIONS: Final[dict[str, str]] = {
    Game.wuwa: "Open-world action RPG by Kuro Games",
    Game.nte: "Urban fantasy open-world RPG",
    Game.bluearchive: "Tactical RPG with anime-style students",
    Game.endfield: "3D sci-fi RPG, sequel to Arknights",
}


class CodeStatus:
    OK: Final[str] = "OK"
    NOT_OK: Final[str] = "NOT_OK"
    UNVERIFIED: Final[str] = "UNVERIFIED"
