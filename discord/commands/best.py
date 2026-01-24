import discord
from discord import app_commands

from clashopt.search import best_comps
from clashopt.bans import simulate_bans
from clashopt.names import canon

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
    if any(c.name == "best" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="best", description="Best comps from your pools.", guild=guild)
    @app_commands.describe(
        enemy="Enemy champs separated by spaces (example: Poppy Janna)",
        ban_model="Ban model name (example: robbery_best_player). Use 'none' for no bans.",
        topk="Candidates per role (search depth).",
        show="How many results to show."
    )
    async def best_cmd(
        interaction: discord.Interaction,
        enemy: str | None = None,
        ban_model: str | None = None,
        topk: int = 10,
        show: int = 5
    ):
        await interaction.response.defer(ephemeral=False)

        enemy_list = enemy.split() if enemy else None

        banned = set()
        bm = (ban_model or "").strip().casefold()
        if bm and bm not in ("none", "null", "no"):
            banned = simulate_bans(bot.ctx.team, bot.ctx.rules, ban_model, seed=0)
            banned = {canon(b, bot.nm) for b in banned}

        out = best_comps(bot.ctx, topk=topk, show=show, banned=banned, enemy=enemy_list)
        if not out:
            await interaction.followup.send("No valid comps found.", ephemeral=False)
            return

        header = []
        if bm and bm not in ("none", "null", "no"):
            header.append(f"**BANNED ({ban_model})**: {', '.join(sorted(banned))}")
        if enemy_list:
            header.append(f"**ENEMY**: {', '.join(enemy_list)}")

        text = ("\n".join(header) + "\n\n") if header else ""
        for i, r in enumerate(out, 1):
            text += f"## #{i}\n{_fmt_comp(r)}\n\n"

        for msg in _chunk(text):
            await interaction.followup.send(msg, ephemeral=False)
