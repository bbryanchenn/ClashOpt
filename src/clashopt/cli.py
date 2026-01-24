import argparse
from .io import load_all
from .validate import validate
from .search import best_comps, resilient_comps, pivot_after_bans
from .bans import simulate_bans
from .report import print_best, print_resilient, print_pivots
from .names import build_name_map, canon

def main():
    ap = argparse.ArgumentParser(prog="clashopt")
    ap.add_argument("--data", default="data")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("best")
    p1.add_argument("--topk", type=int, default=10)
    p1.add_argument("--show", type=int, default=10)
    p1.add_argument("--enemy", nargs="*", default=None)
    p1.add_argument("--ban_model", default=None)

    p2 = sub.add_parser("bans")
    p2.add_argument("--model", default="robbery_best_player")
    p2.add_argument("--seed", type=int, default=0)

    p3 = sub.add_parser("resilient")
    p3.add_argument("--topk", type=int, default=10)
    p3.add_argument("--show", type=int, default=10)
    p3.add_argument("--model", default="robbery_best_player")
    p3.add_argument("--scenarios", type=int, default=50)

    p4 = sub.add_parser("pivot")
    p4.add_argument("--topk", type=int, default=10)
    p4.add_argument("--show", type=int, default=5)
    p4.add_argument("--model", default="robbery_best_player")
    p4.add_argument("--seed", type=int, default=0)

    args = ap.parse_args()
    ctx = load_all(args.data)
    validate(ctx)

    nm = build_name_map(ctx.champ_db)

    if args.cmd == "bans":
        banned = simulate_bans(ctx.team, ctx.rules, args.model, seed=args.seed)
        banned = {canon(b, nm) for b in banned}
        print(", ".join(sorted(banned)) if banned else "(none)")
        return

    if args.cmd == "best":
        banned = set()
        if args.ban_model:
            banned = simulate_bans(ctx.team, ctx.rules, args.ban_model, seed=0)
            banned = {canon(b, nm) for b in banned}
        out = best_comps(ctx, topk=args.topk, show=args.show, banned=banned, enemy=args.enemy)
        print_best(out, banned=banned if banned else None, enemy=args.enemy)
        return

    if args.cmd == "resilient":
        out = resilient_comps(ctx, topk=args.topk, show=args.show, ban_model=args.model, scenarios=args.scenarios)
        print_resilient(out, model=args.model, scenarios=args.scenarios)
        return

    if args.cmd == "pivot":
        base = best_comps(ctx, topk=args.topk, show=1, banned=set(), enemy=None)
        if not base:
            print("No valid comps.")
            return
        base = base[0]
        banned = simulate_bans(ctx.team, ctx.rules, args.model, seed=args.seed)
        banned = {canon(b, nm) for b in banned}
        pivots = pivot_after_bans(ctx, base, banned=banned, topk=args.topk, show=args.show)
        print_pivots(base, banned=banned, pivots=pivots)
        return
