from dataclasses import dataclass

ROLES = ["top", "jungle", "mid", "adc", "support"]

@dataclass(frozen=True)
class Context:
    team: dict
    champ_db: dict
    synergy: dict
    counters: dict
    patch: dict
    rules: dict
