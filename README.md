# Game Codes API

Auto-scrapes game redeem codes from news sites and exposes them via REST API.

## Games

| Slug | Game |
|---|---|
| `wuwa` | Wuthering Waves |
| `nte` | Infinity Nikki |
| `bluearchive` | Blue Archive |
| `endfield` | Arknights: Endfield |

## Endpoints

### `GET /health`

```bash
curl https://game-codes.onrender.com/health
```

```json
{"status":"ok"}
```

### `GET /games`

```bash
curl https://game-codes.onrender.com/games
```

```json
["wuwa","nte","bluearchive","endfield"]
```

### `GET /codes?game=<slug>`

Returns verified (OK) and unverified codes for a game.

```bash
curl https://game-codes.onrender.com/codes?game=nte
```

```json
{
  "game": "nte",
  "codes": [
    {"id": 1, "code": "NTEGIFT", "rewards": "", "source": "scraper"}
  ],
  "unverified": [
    {"id": 2, "code": "NTENEWCODE", "rewards": "", "source": "scraper"}
  ]
}
```

- `codes` — confirmed working
- `unverified` — found on a source site but not yet confirmed

### `POST /codes` (auth required)

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

### `DELETE /codes/{id}` (auth required)

```bash
curl -X DELETE https://game-codes.onrender.com/codes/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

### `POST /update-codes` (auth required)

Triggers an immediate scrape of all sources.

```bash
curl -X POST https://game-codes.onrender.com/update-codes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

### `POST /check-codes` (auth required)

Re-verifies codes against game redemption APIs (only for games that support it).

```bash
curl -X POST https://game-codes.onrender.com/check-codes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```json
{"ok": true}
```

## Auto-scheduling

- **`update-codes`** runs every hour — scrapes sources for new codes, expires codes no longer found
- **`check-codes`** runs daily at 1:30 AM Asia/Taipei — re-verifies codes via game APIs

## Rate Limits

The free Render instance may spin down after inactivity. First request after idle may take a few seconds to wake up.
