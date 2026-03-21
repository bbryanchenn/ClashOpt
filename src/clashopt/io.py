import json
from pathlib import Path
from .model import Context

def _load(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def _extract_relations(champs):
    synergy = {"pairs": []}
    counters = {"champ_vs_champ": []}

    for a, data in champs.items():
        for b, v in data.get("synergy", {}).items():
            if a < b:
                synergy["pairs"].append({"a": a, "b": b, "value": v})

        for b, v in data.get("counters", {}).items():
            counters["champ_vs_champ"].append({"a": a, "b": b, "value": v})

    return synergy, counters


def load_all(data_dir: str) -> Context:
    d = Path(data_dir)

    champs = _load(d / "champion_full.json")
    synergy, counters = _extract_relations(champs)

    return Context(
        team=_load(d / "team.json"),
        champ_db=champs,
        synergy=synergy,
        counters=counters,
        patch=_load(d / "patch.json"),
        rules=_load(d / "draft_rules.json"),
    )