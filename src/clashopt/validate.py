from .names import build_name_map, canon

def validate(ctx):
    nm = build_name_map(ctx.champ_db)

    for p in ctx.team.get("players", []):
        if p.get("role") is None or p.get("name") is None:
            raise ValueError("team.json player missing role/name")
        for c in p.get("pool", []):
            ch = canon(c["champ"], nm)
            if ch not in ctx.champ_db:
                raise KeyError(f"Missing champ_db entry: {ch}")

    for e in ctx.synergy.get("pairs", []):
        canon(e["a"], nm); canon(e["b"], nm)

    for e in ctx.synergy.get("combos", []):
        for ch in e.get("champs", []):
            canon(ch, nm)

    for e in ctx.counters.get("champ_vs_champ", []):
        canon(e["a"], nm); canon(e["b"], nm)
        v = float(e.get("value", 0))
        if not (0.45 <= v <= 0.85):
            raise ValueError(f"Counter WR value looks wrong (expected ~0.45-0.70): {e}")

    for ch, mult in ctx.patch.get("champ_mod", {}).items():
        canon(ch, nm)
        if float(mult) <= 0:
            raise ValueError(f"patch champ_mod must be > 0 for {ch}")

    return True
