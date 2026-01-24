import itertools
from .names import build_name_map, canon
from collections import defaultdict

SYNERGY_SCALE = 10.0
_COUNTERS_BY_TARGET = None

def _pk(a: str, b: str):
    return (a, b) if a < b else (b, a)

def _tags(db: dict, champ: str) -> set[str]:
    return set(db.get(champ, {}).get("tags", []))

def _blind(db: dict, champ: str) -> float:
    return float(db.get(champ, {}).get("blind", 0))

def _diff(db: dict, champ: str) -> float:
    return float(db.get(champ, {}).get("difficulty", 0))

def _dmg(db: dict, champ: str) -> str:
    return db.get(champ, {}).get("damage", "mixed")

def _flex(db: dict, champ: str) -> int:
    return max(0, len(db.get(champ, {}).get("flex_roles", [])) - 1)

def _synergy_map(syn: dict) -> dict:
    m = {}
    for s in syn.get("pairs", []):
        m[_pk(s["a"], s["b"])] = float(s["value"])
    return m

def _counter_map(cnt: dict) -> dict:
    m = {}
    for e in cnt.get("champ_vs_champ", []):
        m[(e["a"], e["b"])] = float(e["value"])
    return m

def _synergy(champs: list[str], smap: dict) -> float:
    return SYNERGY_SCALE * sum(smap.get(_pk(a, b), 0.0) for a, b in itertools.combinations(champs, 2))

def _combo(champs: set[str], syn: dict) -> float:
    v = 0.0
    for c in syn.get("combos", []):
        if all(x in champs for x in c.get("champs", [])):
            v += float(c.get("value", 0))
    return SYNERGY_SCALE * v

def _wincon_fit(rules: dict, tags: set[str]):
    best = (0.0, "none")
    for name, spec in rules.get("wincons", {}).items():
        needs = spec.get("needs", [])
        wants = spec.get("wants", [])
        if any(n not in tags for n in needs):
            continue
        fit = 5.0 * len(needs) + 2.0 * sum(1 for w in wants if w in tags)
        if fit > best[0]:
            best = (fit, name)
    return best

def _damage_profile(damages: list[str]) -> float:
    has_ad = any(d == "ad" for d in damages)
    has_ap = any(d == "ap" for d in damages)
    if has_ad and has_ap:
        return 5.0
    if any(d == "mixed" for d in damages):
        return 3.0
    return 0.0

def _constraints_ok(rules: dict, tags: set[str], damages: list[str]) -> bool:
    c = rules.get("constraints", {})
    for t in c.get("must_have", []):
        if t not in tags:
            return False
    must_any = c.get("must_have_any", [])
    if must_any and not any(t in tags for t in must_any):
        return False

    if c.get("min_mixed_damage"):
        has_ad = any(d in ("ad", "mixed") for d in damages)
        has_ap = any(d in ("ap", "mixed") for d in damages)
        if not (has_ad and has_ap):
            return False

    for rule in c.get("if_has", []):
        if rule.get("tag") in tags:
            for req in rule.get("must_also_have", []):
                if req not in tags:
                    return False
    return True

def _tag_counter(cnt: dict, our_tags: set[str], enemy_tags: set[str]) -> float:
    risk = 0.0
    for r in cnt.get("tag_counters", []):
        if r["threat_tag"] in enemy_tags and r["answer_tag"] not in our_tags:
            risk += float(r["value"])
    return risk

def _champ_counter_wr(cmap: dict, our: list[str], enemy: list[str]) -> float:
    risk = 0.0
    for e in enemy:
        for o in our:
            wr = float(cmap.get((e, o), 0.0))
            risk += max(0.0, wr - 0.50)
    return risk

def normalize_wr(wr: float, games: int) -> float:
    if games >= 80 and (wr < 0.45 or wr > 0.70):
        return 0.75
    return wr

def _wr_points(wr: float, games: int, k: float = 20.0) -> float:
    if games <= 0:
        return 0.0
    wr_s = (wr * games + 0.50 * k) / (games + k)
    return (wr_s - 0.50) * 100.0


def build_counter_index(counters, canon, nm):
    pairs = counters.get("champ_vs_champ", [])
    by_target = defaultdict(list)  # b -> [(a, wr)]
    for e in pairs:
        a = canon(e["a"], nm)
        b = canon(e["b"], nm)
        v = float(e["value"])
        by_target[b].append((a, v))
    for b in by_target:
        by_target[b].sort(key=lambda t: t[1], reverse=True)
    return by_target


def counter_risk_for_comp(comp_champs, by_target, topn: int = 3) -> float:
    risks = []
    for champ in comp_champs:
        lst = by_target.get(champ, [])
        if not lst:
            risks.append(0.0)
            continue
        avg_wr = sum(v for _, v in lst[:topn]) / min(topn, len(lst))
        risks.append(max(0.0, avg_wr - 0.50))  # 0.00 if <=50%
    return sum(risks) / len(risks)  # ~0.00 to ~0.20


def _patch_mult(patch: dict, db: dict, champ: str) -> float:
    m = float(patch.get("champ_mod", {}).get(champ, 1.0))
    tmod = patch.get("tag_mod", {})
    for t in db.get(champ, {}).get("tags", []):
        m *= float(tmod.get(t, 1.0))
    return m

def score(ctx, comp_slots: list[dict], enemy: list[str] | None):
    nm = build_name_map(ctx.champ_db)

    champs = [canon(x["champ"], nm) for x in comp_slots]
    for x, ch in zip(comp_slots, champs):
        x["champ"] = ch

    if enemy:
        enemy = [canon(e, nm) for e in enemy]

    rules = ctx.rules
    w = rules["weights"]
    champ_set = set(champs)

    tags = set()
    for c in champs:
        tags |= _tags(ctx.champ_db, c)
    damages = [_dmg(ctx.champ_db, c) for c in champs]

    if not _constraints_ok(rules, tags, damages):
        return {"score": float("-inf")}

    comfort = sum(float(x.get("comfort", 0)) for x in comp_slots) / 5.0
    role_fit = sum(float(x.get("role_fit", 0)) for x in comp_slots) / 5.0
    synergy = _synergy(champs, _synergy_map(ctx.synergy))
    combo = _combo(champ_set, ctx.synergy)
    win_fit, win_name = _wincon_fit(rules, tags)
    safety = sum(_blind(ctx.champ_db, c) for c in champs) / 5.0
    exec_r = sum(_diff(ctx.champ_db, c) for c in champs) / 5.0
    dmg_score = _damage_profile(damages)
    flex = sum(_flex(ctx.champ_db, c) for c in champs) / 5.0
    patch_score = sum(_patch_mult(ctx.patch, ctx.champ_db, c) for c in champs) / 5.0

    wr_pts = 0.0
    for x in comp_slots:
        games = int(x.get("games", 0))
        wr = normalize_wr(float(x.get("wr", 0.50)), games)
        wr_pts += _wr_points(wr, games)

    wr_pts /= 5.0

    global _COUNTERS_BY_TARGET
    if _COUNTERS_BY_TARGET is None:
        _COUNTERS_BY_TARGET = build_counter_index(ctx.counters, canon, nm)
    #     print("Counter pairs:" , sum(len(v) for v in _COUNTERS_BY_TARGET.values()))

    # print(champs)
    # print("Malphite counters:", _COUNTERS_BY_TARGET .get("Malphite", [])[:3])
    base_ctr = counter_risk_for_comp(champs, _COUNTERS_BY_TARGET, topn=3)

    enemy_ctr = 0.0
    if enemy:
        enemy_tags = set()
        for e in enemy:
            enemy_tags |= _tags(ctx.champ_db, e)
        enemy_ctr += _tag_counter(ctx.counters, tags, enemy_tags)
        enemy_ctr += _champ_counter_wr(_counter_map(ctx.counters), champs, enemy)

    ctr = base_ctr + enemy_ctr


    score_v = (
        w["comfort"] * comfort +
        w["role_fit"] * role_fit +
        w["synergy"] * synergy +
        w["combo"] * combo +
        w["wincon_fit"] * win_fit +
        w["draft_safety"] * safety +
        w["damage_profile"] * dmg_score +
        w["patch"] * patch_score +
        w["flex"] * flex -
        w["counter_risk"] * ctr -
        w["execution_risk"] * exec_r
    )

    return {
        "score": score_v,
        "wincon": win_name,
        "comfort": comfort,
        "role_fit": role_fit,
        "synergy": synergy,
        "combo": combo,
        "draft_safety": safety,
        "execution_risk": exec_r,
        "counter_risk": ctr,
        "damage_profile": dmg_score,
        "patch": patch_score,
        "flex": flex,
        "tags": sorted(tags),
        "comp": comp_slots
    }
