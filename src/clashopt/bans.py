import random
from .model import ROLES

def _flat(team: dict):
    out = []
    for p in team.get("players", []):
        for c in p.get("pool", []):
            out.append((p["name"], p["role"], c["champ"], float(c.get("comfort", 0))))
    return out

def simulate_bans(team: dict, rules: dict, model_name: str, seed: int = 0) -> set[str]:
    random.seed(seed)
    model = rules["ban_models"][model_name]
    bans = int(model.get("bans", 5))
    allc = _flat(team)
    banned: set[str] = set()

    if model.get("per_role"):
        by_role = {r: [] for r in ROLES}
        for rec in allc:
            by_role[rec[1]].append(rec)
        for r in ROLES:
            if not by_role[r]:
                continue
            by_role[r].sort(key=lambda x: x[3], reverse=True)
            banned.add(by_role[r][0][2])
        return set(list(banned)[:bans])

    best_player = model.get("best_player")
    target_n = int(model.get("target_best_player_bans", 0))

    if best_player and target_n > 0:
        bp = [rec for rec in allc if rec[0] == best_player]
        bp.sort(key=lambda x: x[3], reverse=True)
        for rec in bp[:target_n]:
            banned.add(rec[2])

    if len(banned) < bans and model.get("rest_from_team_best_comfort"):
        rem = [rec for rec in allc if rec[2] not in banned]
        rem.sort(key=lambda x: x[3], reverse=True)
        for rec in rem:
            if len(banned) >= bans:
                break
            banned.add(rec[2])

    return set(list(banned)[:bans])
