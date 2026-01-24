import json
from pathlib import Path

def dump(p: Path, obj: dict):
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

if __name__ == "__main__":
    d = Path("data")
    d.mkdir(exist_ok=True)

    dump(d/"team.json", {"players": []})
    dump(d/"champ_db.json", {})
    dump(d/"synergy.json", {"pairs": [], "combos": []})
    dump(d/"counters.json", {"champ_vs_champ": [], "tag_counters": []})
    dump(d/"patch.json", {"champ_mod": {}, "tag_mod": {}})
    dump(d/"draft_rules.json", {"weights": {}, "constraints": {}, "wincons": {}, "ban_models": {}})

    print("Wrote empty placeholders into data/")
