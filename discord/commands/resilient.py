import os
import discord
from discord import app_commands

from clashopt.search import resilient_comps

DEFAULT_MODEL = os.getenv("DEFAULT_BAN_MODEL", "robbery_best_player")

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
    if any(c.name == "resilient" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="resilient", description="Comps that survive a ban model.", guild=guild)
    @app_commands.describe(model="Ban model.", scenarios="Ban simulations.", topk="Search depth.", show="How many.")
    async def resilient_cmd(interaction: discord.Interaction, model: str = DEFAULT_MODEL, scenarios: int = 50, topk: int = 10, show: int = 5):
        await interaction.response.defer(ephemeral=False)
        out = resilient_comps(bot.ctx, topk=topk, show=show, ban_model=model, scenarios=scenarios)
        if not out:
            await interaction.followup.send("No valid comps found.", ephemeral=False)
            return

        text = f"**MODEL** `{model}` | **scenarios** {scenarios}\n\n"
        for i, r in enumerate(out, 1):
            text += f"## #{i}  AVG {r['avg']:.2f}  WORST {r['worst']:.2f}  viable {r['viable']}/{scenarios}\n"
            for x in r["comp"]:
                text += f"`{x['role']:<7}` **{x['player']}** — {x['champ']}\n"
            text += "\n"

        for msg in _chunk(text):
            await interaction.followup.send(msg, ephemeral=False)
