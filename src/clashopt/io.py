import json
from pathlib import Path
from .model import Context

def _load(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_all(data_dir: str) -> Context:
    d = Path(data_dir)
    return Context(
        team=_load(d / "team.json"),
        champ_db=_load(d / "champ_db.json"),
        synergy=_load(d / "synergy.json"),
        counters=_load(d / "counters.json"),
        patch=_load(d / "patch.json"),
        rules=_load(d / "draft_rules.json"),
    )
