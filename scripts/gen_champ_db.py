import json, requests, re
from pathlib import Path

DDRAGON_VERSIONS = "https://ddragon.leagueoflegends.com/api/versions.json"
CHAMP_FULL = "https://ddragon.leagueoflegends.com/cdn/{v}/data/en_US/championFull.json"

ROLES = ["top", "jungle", "mid", "adc", "support"]

def pick_version(v: str | None) -> str:
    if v:
        return v
    return requests.get(DDRAGON_VERSIONS, timeout=20).json()[0]

def dd_tags_to_system(dd_tags: list[str]) -> set[str]:
    out = set()
    if "Tank" in dd_tags:
        out |= {"frontline", "engage", "teamfight"}
    if "Fighter" in dd_tags:
        out |= {"dps", "teamfight"}
    if "Assassin" in dd_tags:
        out |= {"dive", "burst", "pick"}
    if "Mage" in dd_tags:
        out |= {"waveclear", "poke"}
    if "Marksman" in dd_tags:
        out |= {"dps", "scaling", "teamfight"}
    if "Support" in dd_tags:
        out |= {"peel", "vision"}
    return out

def base_damage(dd_tags: list[str]) -> str:
    if "Mage" in dd_tags:
        return "ap"
    if "Marksman" in dd_tags or "Assassin" in dd_tags or "Fighter" in dd_tags:
        return "ad"
    if "Tank" in dd_tags or "Support" in dd_tags:
        return "mixed"
    return "mixed"

def base_range(dd_info: dict) -> str:
    ar = int(dd_info.get("stats", {}).get("attackrange", 0))
    return "ranged" if ar > 200 else "melee"

def base_difficulty(dd_info: dict) -> int:
    return int(dd_info.get("info", {}).get("difficulty", 5))

def base_blind(dd_tags: list[str]) -> int:
    b = 6
    if "Tank" in dd_tags:
        b += 1
    if "Support" in dd_tags:
        b += 1
    if "Assassin" in dd_tags:
        b -= 2
    if "Marksman" in dd_tags:
        b -= 1
    return max(1, min(10, b))

# Manual truth > heuristics (add champs as needed)
FLEX_OVERRIDES: dict[str, list[str]] = {
    "Sett": ["top", "jungle", "support"],
    "Galio": ["mid", "support"],
    "Seraphine": ["support", "mid"],
    "Teemo": ["top", "adc"],
    "Pantheon": ["top", "jungle", "mid", "support"],
    "Gragas": ["top", "jungle", "mid", "support"],
    "Maokai": ["top", "jungle", "support"],
    "Swain": ["mid", "adc", "support"],
    "Taliyah": ["jungle", "mid"],
    "Karthus": ["jungle", "mid"],
    "Ziggs": ["mid", "adc"],
    "Vayne": ["top", "adc"],
    "Kindred": ["jungle", "adc"],
    "Morgana": ["jungle", "support"],
}

def _looks_adc(name: str, dd_tags: list[str], rng: str) -> bool:
    return "Marksman" in dd_tags and rng == "ranged"

def _looks_support(dd_tags: list[str]) -> bool:
    return "Support" in dd_tags

def _looks_mid(dd_tags: list[str]) -> bool:
    return "Mage" in dd_tags or "Assassin" in dd_tags

def _looks_jg(dd_tags: list[str]) -> bool:
    return "Assassin" in dd_tags or "Fighter" in dd_tags or "Tank" in dd_tags

def _looks_top(dd_tags: list[str], rng: str) -> bool:
    return ("Fighter" in dd_tags or "Tank" in dd_tags) and rng == "melee"

def guess_flex_roles(name: str, dd_tags: list[str], rng: str) -> list[str]:
    if name in FLEX_OVERRIDES:
        return FLEX_OVERRIDES[name][:]

    # Safe default: one primary role
    # (We DO NOT want to over-flex everything automatically.)
    if _looks_support(dd_tags):
        return ["support"]
    if _looks_adc(name, dd_tags, rng):
        return ["adc"]
    if _looks_mid(dd_tags):
        return ["mid"]
    if _looks_top(dd_tags, rng):
        return ["top"]
    if _looks_jg(dd_tags):
        return ["jungle"]
    return []

def apply_overrides(name: str, entry: dict, overrides: dict) -> dict:
    o = overrides.get(name)
    if not o:
        return entry

    tags = set(entry["tags"])
    tags |= set(o.get("tags_add", []))
    tags -= set(o.get("tags_remove", []))
    entry["tags"] = sorted(tags)

    for k in ("damage", "blind", "difficulty", "range"):
        if k in o:
            entry[k] = o[k]

    if "flex_roles" in o:
        entry["flex_roles"] = o["flex_roles"]

    return entry

OVERRIDES = {
    "Malphite": {"tags_add": ["wombo"], "damage": "ap", "blind": 8, "difficulty": 2, "flex_roles": ["top"]},
    "Jarvan IV": {"tags_add": ["wombo", "engage"], "damage": "ad", "blind": 7, "difficulty": 4, "flex_roles": ["jungle"]},
    "Galio": {"tags_add": ["wombo", "followup"], "damage": "ap", "blind": 6, "difficulty": 5, "flex_roles": ["mid", "support"]},
    "Twitch": {"tags_add": ["pick"], "blind": 5, "flex_roles": ["adc"]},
    "Ezreal": {"tags_add": ["siege"], "blind": 8, "flex_roles": ["adc"]},
    "Kayn": {"flex_roles": ["jungle"]},
    "Darius": {"flex_roles": ["top"]},
    "Garen": {"flex_roles": ["top"]},
    "Zyra": {"flex_roles": ["support"]},
    "Nami": {"flex_roles": ["support"]},
    "Akali": {"flex_roles": ["mid", "top"]},
}

def main():
    v = pick_version(None)
    data = requests.get(CHAMP_FULL.format(v=v), timeout=30).json()["data"]

    champ_db = {}
    for _, info in data.items():
        name = info["name"]
        dd_tags = info.get("tags", [])
        rng = base_range(info)

        tags = dd_tags_to_system(dd_tags)
        flex_roles = guess_flex_roles(name, dd_tags, rng)

        entry = {
            "tags": sorted(tags),
            "damage": base_damage(dd_tags),
            "range": rng,
            "difficulty": base_difficulty(info),
            "blind": base_blind(dd_tags),
            "flex_roles": flex_roles
        }
        entry = apply_overrides(name, entry, OVERRIDES)
        champ_db[name] = entry

    out = Path("data") / "champ_db.json"
    out.write_text(json.dumps(champ_db, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(champ_db)} champs to {out}")

if __name__ == "__main__":
    main()
