# Game Codes API

[![Status](https://img.shields.io/badge/status-live-brightgreen)](https://game-codes.onrender.com)
[![Render](https://img.shields.io/badge/deployed%20on-Render-46E3B7)](https://render.com)
[![WispByte](https://img.shields.io/badge/deployed%20on-WispByte-6366f1)](https://wispbyte.com)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688)](https://fastapi.tiangolo.com)

Auto-scrapes game redeem codes from news sites. Always up-to-date, refreshed hourly.

**Endpoints:**

| Platform | URL |
|---|---|
| Render | `https://game-codes.onrender.com` |
| WispByte | `https://game-codes.wisp.uno` |

> All examples below use the Render URL. Replace with the WispByte URL if preferred.

---

## Quick Start

```bash
# List all games
curl https://game-codes.onrender.com/games

# Get verified codes for a game
curl https://game-codes.onrender.com/codes?game=nte
```

---

## Games

| Slug | Game | Description | Active Codes |
|---|---|---|---|
| `wuwa` | Wuthering Waves | Open-world action RPG by Kuro Games | 1 verified |
| `nte` | Neverness to Everness | Urban fantasy open-world RPG | 6 verified |
| `bluearchive` | Blue Archive | Tactical RPG with anime-style students | 5 verified |
| `endfield` | Arknights: Endfield | 3D sci-fi RPG, sequel to Arknights | 3 verified |

> Codes expire from source sites over time. The API auto-detects and removes expired codes hourly.

---

## API Reference

### `GET /health`

Check if the service is alive.

```bash
curl https://game-codes.onrender.com/health
```

```json
{"status": "ok"}
```

---

### `GET /games`

List all supported games.

```bash
curl https://game-codes.onrender.com/games
```

```json
{
  "wuwa": {
    "name": "Wuthering Waves",
    "description": "Open-world action RPG by Kuro Games"
  },
  "nte": {
    "name": "Neverness to Everness",
    "description": "Urban fantasy open-world RPG"
  },
  "bluearchive": {
    "name": "Blue Archive",
    "description": "Tactical RPG with anime-style students"
  },
  "endfield": {
    "name": "Arknights: Endfield",
    "description": "3D sci-fi RPG, sequel to Arknights"
  }
}
```

---

### `GET /codes?game={slug}`

Returns verified and unverified codes for a game.

**Parameters:**
- `game` (required) — one of: `wuwa`, `nte`, `bluearchive`, `endfield`

**Response fields:**
- `codes` — confirmed working, safe to redeem
- `unverified` — reported on news sites, not yet confirmed
- `rewards` — reward description (auto-extracted from table sources; may be empty for non-table sources)

```bash
curl https://game-codes.onrender.com/codes?game=nte
```

```json
{
  "game": "nte",
  "codes": [
    {
      "id": 74,
      "code": "LACRIMOSA0603",
      "rewards": "30 Annulith, 20,000 Fons",
      "source": "scraper"
    },
    {
      "id": 76,
      "code": "NTEFUNGAME",
      "rewards": "10,000 Fons",
      "source": "scraper"
    },
    {
      "id": 85,
      "code": "NTEWINFONS",
      "rewards": "10,000 Fons",
      "source": "scraper"
    },
    {
      "id": 90,
      "code": "NTENENE",
      "rewards": "10,000 Clicky Fries, 10 DynamiK",
      "source": "scraper"
    },
    {
      "id": 101,
      "code": "NTEGIFT",
      "rewards": "50 Annulith, 5 Rising Hunter Guides, 5 Light Dye",
      "source": "scraper"
    },
    {
      "id": 102,
      "code": "NTEFREE",
      "rewards": "30,000 Fons",
      "source": "scraper"
    }
  ],
  "unverified": []
}
```

---

### Auth endpoints

Write operations require a Bearer token. Set `API_TOKEN` on the server, then pass it in requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ...
```

#### `POST /codes`

Manually add a code.

```bash
curl -X POST https://game-codes.onrender.com/codes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "MYCODE123", "game": "wuwa"}'
```

```json
{"id": 42, "code": "MYCODE123"}
```

#### `DELETE /codes/{id}`

Remove a code by its ID.

```bash
curl -X DELETE https://game-codes.onrender.com/codes/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

#### `POST /update-codes`

Force an immediate scrape of all source sites.

```bash
curl -X POST https://game-codes.onrender.com/update-codes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

#### `POST /check-codes`

Re-verify codes against game redemption APIs (only for games that support it).

```bash
curl -X POST https://game-codes.onrender.com/check-codes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

---

## Scheduling

The server runs these jobs automatically:

| Job | When | What it does |
|---|---|---|
| `update-codes` | Every hour | Scrapes news sites for new codes, expires codes no longer found |
| `check-codes` | Daily 1:30 AM (Asia/Taipei) | Re-verifies known codes against game redemption APIs |

---

## Error Responses

| Status | Code | When |
|---|---|---|
| `404` | `Unknown game` | Invalid `game` slug |
| `401` | `Invalid token` | Missing or wrong Bearer token |
| `409` | `Code already exists` | Duplicate on `POST /codes` |
| `429` | `Rate limit exceeded` | Too many requests (see below) |

---

## Rate Limits

| Endpoints | Limit | Window |
|---|---|---|
| `GET /health`, `GET /games`, `GET /codes` | 30 requests | per 60 seconds per IP |
| `POST` / `DELETE` (auth required) | unlimited | — |

Exceeding the limit returns `429`:

```json
{"error": "Rate limit exceeded", "retry_after": 60}
```

---

## Source Sites

| Game | Sources |
|---|---|
| WuWa | GamesRadar, GameRant, VG247, PCGamesN, wuthering.gg |
| NTE | GamesRadar, Game8, GameWith |
| Blue Archive | GameRant, Dexerto, Eurogamer, Pocket Tactics |
| Endfield | GamesRadar, Game8 |

---

## Self-Host

```bash
git clone https://github.com/zylo158/game-codes
cd game-codes

python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env with:
#   API_TOKEN=your_token
#   PORT=1078

python run.py
```

Requires Python 3.11+. No database — everything stored in `data.json`.

---

## Notes

- Hosted on Render free tier — may spin down after inactivity. First request may take 3-5s to wake up.
- Codes are stored as a JSON file in the repo. Data resets on deploy but the hourly scheduler re-populates it.
- The scraper filters noise (nav text, common words, product IDs) and detects duplicate patterns automatically.
