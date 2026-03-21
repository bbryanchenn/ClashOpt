import itertools
from .model import ROLES
from .score import score
from .bans import simulate_bans
from .names import build_name_map, canon

def _build_pools(ctx):
    nm = build_name_map(ctx.champ_db)
    pools = {r: [] for r in ROLES}
    for p in ctx.team.get("players", []):
        role = p["role"]
        for c in p.get("pool", []):
            pools[role].append({
                "player": p["name"],
                "role": role,
                "champ": canon(c["champ"], nm),
                "comfort": float(c.get("comfort", 0)),
                "role_fit": float(c.get("role_fit", 0))
            })
    for r in ROLES:
        pools[r].sort(key=lambda x: (x["comfort"], x["role_fit"]), reverse=True)
    return pools

def best_comps(ctx, topk: int, show: int, banned: set[str], enemy: list[str] | None):
    nm = build_name_map(ctx.champ_db)
    banned = set(canon(b, nm) for b in (banned or [])) 
    enemy = [canon(e, nm) for e in enemy] if enemy else None

    pools = _build_pools(ctx)
    role_lists = []
    for r in ROLES:
        cand = [x for x in pools[r] if x["champ"] not in banned][:max(1, topk)]
        role_lists.append(cand)

    out = []
    for picks in itertools.product(*role_lists):
        champs = [p["champ"] for p in picks]
        if len(set(champs)) != 5:
            continue
        r = score(ctx, list(picks), enemy)
        if r["score"] != float("-inf"):
            out.append(r)

    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:show]

def resilient_comps(ctx, topk: int, show: int, ban_model: str, scenarios: int):
    pools = _build_pools(ctx)
    role_lists = [pools[r][:max(1, topk)] for r in ROLES]

    base = []
    for picks in itertools.product(*role_lists):
        champs = [p["champ"] for p in picks]
        if len(set(champs)) != 5:
            continue
        base.append(list(picks))

    out = []
    for comp in base:
        champs = {x["champ"] for x in comp}
        scores = []
        for s in range(scenarios):
            banned = simulate_bans(ctx.team, ctx.rules, ban_model, seed=s)
            nm = build_name_map(ctx.champ_db)
            banned = {canon(b, nm) for b in banned}
            if champs & banned:
                scores.append(float("-inf"))
                continue
            scores.append(score(ctx, comp, enemy=None)["score"])
        out.append({
            "avg": sum(scores) / len(scores),
            "worst": min(scores),
            "viable": sum(1 for x in scores if x != float("-inf")),
            "comp": comp
        })

    out.sort(key=lambda x: (x["avg"], x["viable"], x["worst"]), reverse=True)
    return out[:show]

def pivot_after_bans(ctx, base_comp: dict, banned: set[str], topk: int = 10, show: int = 5):
    base_champs = {x["champ"] for x in base_comp["comp"]}
    candidates = best_comps(ctx, topk=topk, show=200, banned=banned, enemy=None)
    pivots = []
    for r in candidates:
        champs = {x["champ"] for x in r["comp"]}
        overlap = len(base_champs & champs)
        pivots.append((overlap, r["score"], r))
    pivots.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [x[2] for x in pivots[:show]]
