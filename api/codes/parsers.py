from __future__ import annotations

import re
from typing import Callable

from bs4 import BeautifulSoup, Tag

from api.codes.sources import CodeSource

ParserFunc = Callable[[str], list[dict]]

SELECTORS: dict[CodeSource, str] = {
    CodeSource.GAMESRADAR: ".article-body",
    CodeSource.GAME8: ".archive-style-wrapper",
    CodeSource.GAMEWITH: ".article-wrap",
    CodeSource.DEXERTO: "article",
    CodeSource.PCGAMESN: ".entry-content",
    CodeSource.WUTHERINGGG: ".codes-table",
    CodeSource.EUROGAMER: ".article_body_content",
    CodeSource.POCKETTACTICS: ".entry-content",
    CodeSource.POLYGON: ".article-body",
}

_VALID_CODE = re.compile(r"^[A-Z0-9_]{4,}$")


def _is_valid_code(s: str) -> bool:
    return bool(_VALID_CODE.match(s))


def _container(soup: BeautifulSoup, selector: str) -> Tag | BeautifulSoup:
    el = soup.select_one(selector)
    return el if el else soup


def _heading_has_expired(tag: Tag) -> bool:
    heading = tag.find_previous(["h1", "h2", "h3", "h4", "h5", "h6", "a"])
    return bool(heading and "expir" in heading.get_text(strip=True).lower())


def _sanitize_code(raw: str) -> str:
    code = raw.strip().split("/")[0].strip()
    code = re.sub(r"\s*\(.*?\)", "", code)
    code = re.sub(r"\s*\[.*?\]", "", code)
    code = code.upper().strip()
    return code


def _find_li_content(li: Tag) -> tuple[str, str]:
    strong = li.find("strong")
    if not strong:
        return "", ""
    code = _sanitize_code(strong.get_text(strip=True))
    if not code or len(code) < 4:
        return "", ""
    li_text = li.get_text(" ", strip=True)
    strong_text = strong.get_text(strip=True)
    if li_text.startswith(strong_text):
        after = li_text[len(strong_text):]
    else:
        idx = li_text.find(code)
        if idx == -1:
            return code, ""
        after = li_text[idx + len(code):]
    after = re.sub(r"^[\s:–\-|,;.]+", "", after).strip()
    return code, after


def parse_gamesradar(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.GAMESRADAR])
    results: list[dict] = []
    seen: set[str] = set()
    passed_livestream = False
    for li in container.find_all("li"):
        if _heading_has_expired(li) or passed_livestream:
            continue
        code, rewards = _find_li_content(li)
        if code and _is_valid_code(code) and code not in seen:
            li_text = li.get_text(" ", strip=True)
            idx = li_text.upper().find(code)
            if idx >= 0:
                after = li_text[idx + len(code):]
                if "livestream" in after.lower() or "live stream" in after.lower():
                    passed_livestream = True
                    continue
            seen.add(code)
            results.append({"code": code, "rewards": rewards})
    return results


def parse_polygon(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.POLYGON])
    results: list[dict] = []
    seen: set[str] = set()
    for li in container.find_all("li"):
        if _heading_has_expired(li):
            continue
        code, rewards = _find_li_content(li)
        if code and _is_valid_code(code) and code not in seen:
            seen.add(code)
            results.append({"code": code, "rewards": rewards})
    return results


def parse_eurogamer(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.EUROGAMER])
    results: list[dict] = []
    seen: set[str] = set()
    for li in container.find_all("li"):
        if _heading_has_expired(li):
            continue
        text = li.get_text(" ", strip=True)
        if ":" not in text or len(text) > 200:
            continue
        parts = text.split(":", 1)
        code = parts[0].strip().split("/")[0].strip()
        if not _is_valid_code(code):
            continue
        rewards = parts[1].strip()
        if code not in seen:
            seen.add(code)
            results.append({"code": code, "rewards": rewards})
    return results


def parse_pockettactics(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.POCKETTACTICS])
    results: list[dict] = []
    seen: set[str] = set()
    for li in container.find_all("li"):
        if _heading_has_expired(li):
            continue
        code, rewards = _find_li_content(li)
        if code and _is_valid_code(code) and code not in seen:
            seen.add(code)
            results.append({"code": code, "rewards": rewards or ""})
    return results


def parse_game8(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.GAME8])
    results: list[dict] = []
    seen: set[str] = set()
    for table in container.find_all("table", class_="a-table"):
        if _heading_has_expired(table):
            continue
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            code_div = cells[0].find("div", class_="a-clipboard__container")
            if code_div:
                code = code_div.get_text(strip=True)
            else:
                code = cells[0].get_text(strip=True)
            if not _is_valid_code(code):
                continue
            reward_divs = cells[1].find_all("div", class_="align")
            if reward_divs:
                rewards = " ".join(d.get_text(strip=True) for d in reward_divs)
            else:
                rewards = cells[1].get_text(" ", strip=True)
            if code not in seen:
                seen.add(code)
                results.append({"code": code, "rewards": rewards})
    return results


def parse_gamewith(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.GAMEWITH])
    results: list[dict] = []
    seen: set[str] = set()
    for table in container.find_all("table"):
        thead = table.find("th")
        if not thead:
            continue
        if "code" not in thead.get_text(strip=True).lower():
            continue
        if _heading_has_expired(table):
            continue
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            raw = cells[0].get_text(strip=True)
            if not raw or not _is_valid_code(raw):
                continue
            code = raw
            half = len(code) // 2
            if len(code) >= 8 and len(code) % 2 == 0 and code[:half] == code[half:]:
                code = code[:half]
            rewards = cells[1].get_text(strip=True)
            if code not in seen:
                seen.add(code)
                results.append({"code": code, "rewards": rewards})
    return results


def parse_pcgamesn(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.PCGAMESN])
    results: list[dict] = []
    seen: set[str] = set()
    for p in container.find_all("p"):
        text = p.get_text(" ", strip=True)
        if "expir" in text.lower():
            continue
        for match in re.finditer(r"\b([A-Z0-9_]{4,})\s*[-–]\s*(.+)", text):
            code = _sanitize_code(match.group(1))
            rewards = match.group(2).strip()
            if code and _is_valid_code(code) and code not in seen:
                seen.add(code)
                results.append({"code": code, "rewards": rewards})
    return results


def parse_wutheringgg(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one(SELECTORS[CodeSource.WUTHERINGGG])
    if not table:
        return []
    results: list[dict] = []
    seen: set[str] = set()
    for row in table.find_all("tr", class_="active"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        code = cells[0].get_text(strip=True)
        reward_td = cells[2]
        rewards = reward_td.get_text(" ", strip=True)
        if code and _is_valid_code(code) and code not in seen:
            seen.add(code)
            results.append({"code": code, "rewards": rewards})
    return results


def parse_dexerto(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    container = _container(soup, SELECTORS[CodeSource.DEXERTO])
    results: list[dict] = []
    seen: set[str] = set()
    for strong in container.find_all(["strong", "b"]):
        if _heading_has_expired(strong):
            continue
        text = strong.get_text(strip=True)
        code = text.split("/")[0].strip()
        if not _is_valid_code(code):
            continue
        parent = strong.parent
        rewards = ""
        if parent:
            parent_text = parent.get_text(" ", strip=True)
            m = re.search(
                r"\b" + re.escape(code) + r"\b\s*[-–:]\s*(.*)", parent_text
            )
            if m:
                rewards = m.group(1).strip()
        if code not in seen:
            seen.add(code)
            results.append({"code": code, "rewards": rewards})
    return results


_PARSERS: dict[CodeSource, ParserFunc] = {
    CodeSource.GAMESRADAR: parse_gamesradar,
    CodeSource.GAME8: parse_game8,
    CodeSource.GAMEWITH: parse_gamewith,
    CodeSource.DEXERTO: parse_dexerto,
    CodeSource.PCGAMESN: parse_pcgamesn,
    CodeSource.WUTHERINGGG: parse_wutheringgg,
    CodeSource.EUROGAMER: parse_eurogamer,
    CodeSource.POCKETTACTICS: parse_pockettactics,
    CodeSource.POLYGON: parse_polygon,
}


def get_parser(source: str) -> ParserFunc | None:
    try:
        return _PARSERS.get(CodeSource(source))
    except ValueError:
        return None
