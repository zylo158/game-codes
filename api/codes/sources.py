from __future__ import annotations

from enum import StrEnum
from typing import Final

from api.constants import Game


class CodeSource(StrEnum):
    GAMESRADAR = "gamesradar"
    GAMERANT = "gamerant"
    GAME8 = "game8"
    GAMEWITH = "gamewith"
    DEXERTO = "dexerto"
    PCGAMESN = "pcgamesn"
    VG247 = "vg247"
    WUTHERINGGG = "wutheringgg"
    EUROGAMER = "eurogamer"
    POCKETTACTICS = "pockettactics"
    GAMESPOT = "gamespot"
    PCGAMER = "pcgamer"
    POCKETGAMER = "pocketgamer"


CODE_URLS: Final[dict[str, dict[CodeSource, str]]] = {
    Game.wuwa: {
        CodeSource.GAMESRADAR: "https://www.gamesradar.com/games/rpg/wuthering-waves-codes-redeem/",
        CodeSource.GAMERANT: "https://gamerant.com/wuthering-waves-codes/",
        CodeSource.WUTHERINGGG: "https://wuthering.gg/codes",
        CodeSource.VG247: "https://www.vg247.com/wuthering-waves-codes-redeem",
        CodeSource.PCGAMESN: "https://www.pcgamesn.com/wuthering-waves/codes",
        CodeSource.GAME8: "https://game8.co/games/Wuthering-Waves/archives/453149",
    },
    Game.nte: {
        CodeSource.GAMESRADAR: "https://www.gamesradar.com/games/action-rpg/neverness-to-everness-codes-nte/",
        CodeSource.GAME8: "https://game8.co/games/Neverness-to-Everness/archives/593718",
        CodeSource.GAMEWITH: "https://gamewith.net/nte/74145",
        CodeSource.GAMESPOT: "https://www.gamespot.com/articles/neverness-to-everness-codes/1100-6539804/",
        CodeSource.GAMERANT: "https://gamerant.com/neverness-to-everness-nte-redeem-code-redemption-promo-livestream-gift-annulith/",
        CodeSource.DEXERTO: "https://www.dexerto.com/wikis/neverness-to-everness/nte-codes/",
    },
    Game.bluearchive: {
        CodeSource.GAMERANT: "https://gamerant.com/blue-archive-codes/",
        CodeSource.DEXERTO: "https://www.dexerto.com/codes/blue-archive-codes-3311458/",
        CodeSource.EUROGAMER: "https://www.eurogamer.net/blue-archive-codes",
        CodeSource.POCKETTACTICS: "https://www.pockettactics.com/blue-archive/codes",
        CodeSource.PCGAMER: "https://www.pcgamer.com/games/strategy/blue-archive-codes/",
        CodeSource.POCKETGAMER: "https://www.pocketgamer.com/blue-archive/coupon-codes/",
    },
    Game.endfield: {
        CodeSource.GAMESRADAR: "https://www.gamesradar.com/games/rpg/arknights-endfield-codes/",
        CodeSource.GAME8: "https://game8.co/games/Arknights-Endfield/archives/571509",
        CodeSource.PCGAMER: "https://www.pcgamer.com/games/rpg/arknights-endfield-codes-redeem/",
        CodeSource.POCKETTACTICS: "https://www.pockettactics.com/arknights-endfield/codes",
    },
}
