from __future__ import annotations

import argparse
import os
from .bans import simulate_bans
from .io import load_all
from .names import build_name_map, canon
from .report import print_best, print_pivots, print_resilient
from .search import best_comps, pivot_after_bans, resilient_comps
from .validate import validate


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="clashopt")
    ap.add_argument("--data", default="data")

    sub = ap.add_subparsers(dest="cmd", required=True)

    p_best = sub.add_parser("best")
    p_best.add_argument("--topk", type=int, default=10)
    p_best.add_argument("--show", type=int, default=10)
    p_best.add_argument("--enemy", nargs="*", default=None)
    p_best.add_argument("--ban_model", default=None)

    p_bans = sub.add_parser("bans")
    p_bans.add_argument("--model", default="robbery_best_player")
    p_bans.add_argument("--seed", type=int, default=0)
    p_bans.add_argument("--banned", nargs="*", default=[], help="Champs banned (remove from pool)")

    p_res = sub.add_parser("resilient")
    p_res.add_argument("--topk", type=int, default=10)
    p_res.add_argument("--show", type=int, default=10)
    p_res.add_argument("--model", default="robbery_best_player")
    p_res.add_argument("--scenarios", type=int, default=50)

    p_pivot = sub.add_parser("pivot")
    p_pivot.add_argument("--topk", type=int, default=10)
    p_pivot.add_argument("--show", type=int, default=5)
    p_pivot.add_argument("--model", default="robbery_best_player")
    p_pivot.add_argument("--seed", type=int, default=0)

    return ap


def _canon_set(champs: set[str], nm: dict[str, str]) -> set[str]:
    return {canon(c, nm) for c in champs}


def main() -> None:
    args = _build_parser().parse_args()

    ctx = load_all(args.data)
    validate(ctx)
    nm = build_name_map(ctx.champ_db)

    match args.cmd:
        case "bans":
            banned = simulate_bans(ctx.team, ctx.rules, args.model, seed=args.seed)
            banned = _canon_set(set(banned), nm)
            print(", ".join(sorted(banned)) if banned else "(none)")

        case "best":
            banned: set[str] = set()
            if args.ban_model:
                banned = simulate_bans(ctx.team, ctx.rules, args.ban_model, seed=0)
                banned = _canon_set(set(banned), nm)

            out = best_comps(
                ctx,
                topk=args.topk,
                show=args.show,
                banned=args.banned,
                enemy=args.enemy,
            )
            print_best(out, banned=banned or None, enemy=args.enemy)

        case "resilient":
            out = resilient_comps(
                ctx,
                topk=args.topk,
                show=args.show,
                ban_model=args.model,
                scenarios=args.scenarios,
            )
            print_resilient(out, model=args.model, scenarios=args.scenarios)

        case "pivot":
            base = best_comps(ctx, topk=args.topk, show=1, banned=set(), enemy=None)
            if not base:
                print("No valid comps.")
                return

            base = base[0]
            banned = simulate_bans(ctx.team, ctx.rules, args.model, seed=args.seed)
            banned = _canon_set(set(banned), nm)

            pivots = pivot_after_bans(ctx, base, banned=banned, topk=args.topk, show=args.show)
            print_pivots(base, banned=banned, pivots=pivots)

        case _:
            raise SystemExit(f"Unknown command: {args.cmd}")
