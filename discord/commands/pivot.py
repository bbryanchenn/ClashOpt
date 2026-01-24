import os
import discord
from discord import app_commands

from clashopt.search import best_comps, pivot_after_bans
from clashopt.bans import simulate_bans
from clashopt.names import canon

DEFAULT_MODEL = os.getenv("DEFAULT_BAN_MODEL", "robbery_best_player")

def _fmt_comp(r: dict) -> str:
    lines = [f"**SCORE** {r['score']:.2f} | wincon `{r.get('wincon','?')}` | syn {r.get('synergy',0):.2f} | ctr {r.get('counter_risk',0):.2f}"]
    for x in r["comp"]:
        lines.append(f"`{x['role']:<7}` **{x['player']}** — {x['champ']}")
    return "\n".join(lines)

def _chunk(text: str, limit: int = 1900):
    out, cur = [], ""
    for line in text.splitlines():
        if len(cur) + len(line) + 1 > limit:
            out.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        out.append(cur)
    return out

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "pivot" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="pivot", description="Base comp → bans → best pivots.", guild=guild)
    @app_commands.describe(model="Ban model.", seed="Ban seed.", topk="Search depth.", show="Pivots to show.")
    async def pivot_cmd(interaction: discord.Interaction, model: str = DEFAULT_MODEL, seed: int = 0, topk: int = 10, show: int = 5):
        await interaction.response.defer(ephemeral=False)

        base_list = best_comps(bot.ctx, topk=topk, show=1, banned=set(), enemy=None)
        if not base_list:
            await interaction.followup.send("No base comp found.", ephemeral=False)
            return
        base = base_list[0]

        banned = simulate_bans(bot.ctx.team, bot.ctx.rules, model, seed=seed)
        banned = {canon(b, bot.nm) for b in banned}

        pivots = pivot_after_bans(bot.ctx, base, banned=banned, topk=topk, show=show)

        text = "## BASE\n" + _fmt_comp(base) + "\n\n"
        text += f"## BANNED ({model}, seed={seed})\n{', '.join(sorted(banned)) if banned else '(none)'}\n\n"
        text += "## PIVOTS\n"
        if not pivots:
            text += "No pivots found.\n"
        else:
            for i, r in enumerate(pivots, 1):
                text += f"### Pivot #{i}\n{_fmt_comp(r)}\n\n"

        for msg in _chunk(text):
            await interaction.followup.send(msg, ephemeral=False)
