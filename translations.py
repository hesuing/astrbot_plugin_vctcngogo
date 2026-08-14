_AGENTS_CN = {
    "jett": "捷风",
    "raze": "雷兹",
    "reyna": "芮娜",
    "neon": "霓虹",
    "phoenix": "不死鸟",
    "yoru": "夜露",
    "iso": "艾索",
    "sova": "猎枭",
    "breach": "叛奇",
    "skye": "斯凯",
    "fade": "菲德",
    "gekko": "盖可",
    "kayo": "KAY/O",
    "k-o": "KAY/O",
    "omen": "幽影",
    "brimstone": "布史东",
    "viper": "蝰蛇",
    "astra": "亚星卓",
    "harbor": "哈泊",
    "clove": "可芙",
    "sage": "贤者",
    "cypher": "零",
    "killjoy": "奇乐",
    "chamber": "钱博尔",
    "deadlock": "黛丝",
    "vyse": "薇斯",
    "tejo": "特哈",
    "waylay": "薇拉",
}


def _cn_agent(slug: str) -> str:
    return _AGENTS_CN.get((slug or "").strip().lower(), slug or "")


_MAPS_CN = {
    "sunset": "日落之城",
    "lotus": "莲花古城",
    "pearl": "深海明珠",
    "fracture": "热带乐园",
    "breeze": "微风岛屿",
    "icebox": "极地寒港",
    "bind": "隐世修所",
    "haven": "霓虹町",
    "split": "裂变峡谷",
    "ascent": "亚海悬城",
    "abyss": "幽邃地窟",
    "district": "商贸区",
    "drift": "漂移",
    "glitch": "故障",
    "plaza": "广场",
    "tibet": "藏身所",
}


def _cn_map(slug: str) -> str:
    return _MAPS_CN.get((slug or "").strip().lower(), slug or "")