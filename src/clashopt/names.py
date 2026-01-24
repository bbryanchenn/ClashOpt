import re

ALIASES = {
    "drmundo": "Dr. Mundo",
    "jarvaniv": "Jarvan IV",
    "kogmaw": "Kog'Maw",
    "leblanc": "LeBlanc",
    "masteryi": "Master Yi",
    "missfortune": "Miss Fortune",
    "reksai": "Rek'Sai",
    "tahmkench": "Tahm Kench",
    "twistedfate": "Twisted Fate",
    "velkoz": "Vel'Koz",
    "khazix": "Kha'Zix",
    "belveth": "Bel'Veth",
    "kaisa": "Kai'Sa"
}

def norm(name: str) -> str:
    s = name.strip()
    s = re.sub(r"\s+", " ", s)
    return s.casefold()

def build_name_map(champ_db: dict) -> dict[str, str]:
    m: dict[str, str] = {}
    for k in champ_db.keys():
        nk = norm(k)
        if nk not in m:
            m[nk] = k
    return m

def canon(name: str, name_map: dict[str, str]) -> str:
    key = norm(name)
    key = norm(ALIASES.get(key, name))
    if key not in name_map:
        raise KeyError(f"Unknown champ: {name}")
    return name_map[key]

