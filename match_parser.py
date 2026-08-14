from __future__ import annotations

import re
import urllib.request

try:
    from .translations import _cn_map
except ImportError:
    from translations import _cn_map

REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "text/html, */*",
}


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "")
    return s.strip()


def fetch(url: str, referer: str = "") -> str:
    headers = dict(REQ_HEADERS)
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


fetch_page_html = fetch


def _get_real_match_id(match_page_html: str) -> str | None:
    m = re.search(r'data-match-id="(\d+)"', match_page_html)
    return m.group(1) if m else None


def parse_match_page(html: str) -> dict | None:
    """解析比赛详情页 HTML，返回 match_id 与比分信息。"""
    mid = re.search(r'data-match-id="(\d+)"', html)
    if not mid:
        return None
    result = {"match_id": mid.group(1)}

    # 总比分 header
    m = re.search(
        r'match-header-vs-score">.*?'
        r'match-header-vs-score-winner">\s*(\d+)\s*</span>'
        r'\s*<span class="match-header-vs-score-colon">\s*:\s*</span>'
        r'\s*<span class="match-header-vs-score-loser">\s*(\d+)\s*</span>',
        html,
        re.S,
    )
    if m:
        result["score"] = (m.group(1), m.group(2))
    note = re.search(r'match-header-vs-note">\s*([^<]+?)\s*<', html)
    if note:
        result["header_note"] = note.group(1).strip()
    return result


def parse_overview(html: str) -> list[dict]:
    """解析 /match/tab/overview 返回的 HTML，提取每张图的完整数据。

    返回 [{map: str, game_id: str, scores: [..], halves: [(ct,t)..],
            teams: [..], winner: str, players: [...]}]
    """
    games = []
    blocks = re.split(
        r'(?=<div class="vm-stats-game[^"]*"[^>]*data-game-id=")', html
    )
    for b in blocks:
        gid_m = re.search(r'data-game-id="([^"]+)"', b)
        if not gid_m:
            continue
        gid = gid_m.group(1)
        if gid == "all":
            continue

        mp = re.findall(
            r'font-weight: 700[^>]*>\s*<span[^>]*>\s*([A-Za-z ]+?)\s*<', b
        )
        teams = []
        scores = {}
        # 左队: <div class="team"> ... team-name ... mod-ct / mod-t
        left = re.search(
            r'<div class="team">.*?class="team-name">\s*([^<]+?)\s*<'
            r'.*?<span class="mod-ct">(\d+)</span>\s*/\s*<span class="mod-t">(\d+)</span>',
            b,
            re.S,
        )
        if left:
            name = left.group(1).strip()
            teams.append(name)
            scores[name] = {
                "ct": int(left.group(2)),
                "t": int(left.group(3)),
                "total": int(left.group(2)) + int(left.group(3)),
            }
        # 右队: <div class="team mod-right"> ... team-name ... mod-t / mod-ct
        right = re.search(
            r'<div class="team mod-right">.*?class="team-name">\s*([^<]+?)\s*<'
            r'.*?<span class="mod-t">(\d+)</span>\s*/\s*<span class="mod-ct">(\d+)</span>',
            b,
            re.S,
        )
        if right:
            name = right.group(1).strip()
            teams.append(name)
            scores[name] = {
                "ct": int(right.group(3)),
                "t": int(right.group(2)),
                "total": int(right.group(2)) + int(right.group(3)),
            }
        winner = ""
        if len(teams) == 2 and scores[teams[0]]["total"] != scores[teams[1]]["total"]:
            winner = max(teams, key=lambda t: scores[t]["total"])
        players_raw = re.findall(
            r'ovw-player-name text-of">\s*([^<]+?)\s*<[^>]*>'
            r'\s*<div class="ovw-player-tag ge-text-light">\s*([^<]+?)\s*<'
            r'.*?agents[^>]*>\s*<span class="stats-sq mod-agent small">'
            r'\s*<img src="/img/vlr/game/agents/([a-z_0-9]+)\.png"',
            b,
            re.S,
        )
        ratings = re.findall(
            r'data-col="rating2"><span class="stats-sq">\s*'
            r'<span class="side mod-both">([0-9.]+)</span>',
            b,
        )
        acs_list = re.findall(
            r'data-col="acs"><span class="stats-sq">\s*'
            r'<span class="side mod-both">(\d+)</span>',
            b,
        )
        kda_list = re.findall(
            r'data-col="kills"><span class="side mod-both">(\d+)</span>'
            r'.*?data-col="deaths"><span class="side mod-both">(\d+)</span>'
            r'.*?data-col="assists"><span class="side mod-both">(\d+)</span>',
            b,
            re.S,
        )

        players = []
        for i, p in enumerate(players_raw):
            players.append(
                {
                    "name": _clean(p[0]),
                    "team": _clean(p[1]),
                    "agent": _clean(p[2]),
                    "rating": float(ratings[i]) if i < len(ratings) else 0.0,
                    "acs": int(acs_list[i]) if i < len(acs_list) else 0,
                    "kills": int(kda_list[i][0]) if i < len(kda_list) else 0,
                    "deaths": int(kda_list[i][1]) if i < len(kda_list) else 0,
                    "assists": int(kda_list[i][2]) if i < len(kda_list) else 0,
                }
            )

        

        games.append(
            {
                "map": mp[0].strip() if mp else "",
                "map_cn": _cn_map(mp[0].strip()) if mp else "",
                "game_id": gid,
                "teams": teams,
                "scores": scores,
                "winner": winner,
                "players": players,
            }
        )
    return games


def fetch_overview(match_id: str, game_id: str = "all", referer: str = "") -> str:
    url = (
        f"https://www.vlr.gg/match/tab/overview"
        f"?match_id={match_id}&game_id={game_id}"
    )
    return fetch(url, referer=referer)


def fetch_match_details(url_id: str) -> dict:
    """抓取整场比赛详情。

    返回 {url_id, match_id, match_html, info, games}
    match_id 为 vlr 的内部 ID(与 URL 数字不同)，用于 overview 接口。
    """
    page_url = f"https://www.vlr.gg/{url_id}"
    match_html = fetch(page_url, referer=page_url)
    real_id = _get_real_match_id(match_html)
    info = parse_match_page(match_html)
    games = []
    if real_id:
        try:
            ov_html = fetch_overview(real_id, referer=page_url)
            games = parse_overview(ov_html)
        except Exception:  # noqa: BLE001
            games = []
    return {
        "url_id": url_id,
        "match_id": real_id,
        "match_html": match_html,
        "info": info,
        "games": games,
    }
