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
        # 仅取 header 区域（到轮次手走势图为止），避免跨界污染
        hd = b[b.find("vm-stats-game-header") :]
        r_idx = hd.find("vlr-rounds")
        if r_idx != -1:
            hd = hd[:r_idx]
        mr_idx = hd.find('<div class="team mod-right">')

        def _side(name_m, total_m, part, default_total=0):
            """从队伍块提取 名称 + {ct,t,total}，不依赖 mod 先后顺序。"""
            if not name_m:
                return None
            name = name_m.group(1).strip()
            ct_m = re.search(r'<span class="mod-ct">(\d+)</span>', part)
            t_m = re.search(r'<span class="mod-t">(\d+)</span>', part)
            ct = int(ct_m.group(1)) if ct_m else 0
            t = int(t_m.group(1)) if t_m else 0
            if ct or t:
                total = ct + t
            else:
                total = int(total_m.group(1)) if total_m else default_total
            return name, {"ct": ct, "t": t, "total": total}

        left_part = hd[:mr_idx] if mr_idx != -1 else hd
        left = _side(
            re.search(r'<div class="team-name">\s*([^<]+?)\s*<', left_part),
            re.search(
                r'<div class="score[^"]*"\s*style="[^"]*margin-right\s*:\s*12px[^"]*">\s*(\d+)',
                left_part,
            ),
            left_part,
        )
        if left:
            teams.append(left[0])
            scores[left[0]] = left[1]
        if mr_idx != -1:
            right_part = hd[mr_idx:]
            right = _side(
                re.search(
                    r'<div class="team mod-right">.*?<div class="team-name">\s*([^<]+?)\s*<',
                    right_part,
                    re.S,
                ),
                re.search(
                    r'<div class="score[^"]*"\s*style="[^"]*margin-left\s*:\s*8px[^"]*">\s*(\d+)',
                    right_part,
                ),
                right_part,
            )
            if right:
                teams.append(right[0])
                scores[right[0]] = right[1]
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
