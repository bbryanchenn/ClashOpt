def print_best(results, banned=None, enemy=None):
    if banned:
        print("BANNED:", ", ".join(sorted(banned)))
    if enemy:
        print("ENEMY:", ", ".join(enemy))
    for i, r in enumerate(results, 1):
        print(f"\n#{i} SCORE {r['score']:.2f} wincon={r['wincon']} comfort={r['comfort']:.2f} syn={r['synergy']:.2f} ctr={r['counter_risk']:.2f}")
        for x in r["comp"]:
            print(f"  {x['role']:<7} {x['player']:<12} {x['champ']}")

def print_resilient(results, model, scenarios):
    print(f"MODEL={model} scenarios={scenarios}")
    for i, r in enumerate(results, 1):
        print(f"\n#{i} AVG {r['avg']:.2f} WORST {r['worst']:.2f} viable {r['viable']}/{scenarios}")
        for x in r["comp"]:
            print(f"  {x['role']:<7} {x['player']:<12} {x['champ']}")

def print_pivots(base, banned, pivots):
    print("BASE:")
    print_best([base], banned=None, enemy=None)
    print("\nBANNED:", ", ".join(sorted(banned)) if banned else "(none)")
    print("\nPIVOTS:")
    print_best(pivots, banned=None, enemy=None)
