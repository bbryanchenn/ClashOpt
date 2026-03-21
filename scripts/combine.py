import json
from pathlib import Path

BASE = Path(r"C:\Users\heint\OneDrive\Documents\CodesNStuffz\clashTeam\data")

CHAMPDB_PATH = BASE / "champ_db.json"
COUNTERS_PATH = BASE / "counters.json"
SYNERGY_PATH = BASE / "synergy.json"
OUTPUT_PATH = BASE / "champion_full.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_champ(store, champ):
    if champ not in store:
        store[champ] = {
            "tags": [],
            "damage": None,
            "range": None,
            "difficulty": None,
            "blind": None,
            "flex_roles": [],
            "synergy": {},
            "counters": {},
            "combos": []
        }
def norm(name):
    return name.lower().replace("'", "").replace(" ", "")

def main():
    
    champdb = load_json(CHAMPDB_PATH)
    name_map = {norm(champ): champ for champ in champdb}
    
    counters = load_json(COUNTERS_PATH)
    synergy = load_json(SYNERGY_PATH)

    merged = {}

    for champ, meta in champdb.items():
        merged[champ] = {
            **meta,
            "synergy": {},
            "counters": {},
            "combos": []
        }

    for row in counters.get("champ_vs_champ", []):
        a = name_map.get(norm(row["a"]))
        b = name_map.get(norm(row["b"]))
        v = row["value"]

        if not a or not b:
            continue

        merged[a]["counters"][b] = v

        merged[a]["counters"][b] = v

    for row in synergy.get("pairs", []):
        a = name_map.get(norm(row["a"]))
        b = name_map.get(norm(row["b"]))
        v = row["value"]

        if not a or not b:
            continue

        merged[a]["synergy"][b] = v
        merged[b]["synergy"][a] = v

    for combo in synergy.get("combos", []):
        champs = [name_map.get(norm(c)) for c in combo.get("champs", [])]
        champs = [c for c in champs if c]

        for champ in champs:
            merged[champ]["combos"].append({
                **combo,
                "champs": champs
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print("done:", OUTPUT_PATH)


if __name__ == "__main__":
    main()