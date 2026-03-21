import os
import discord
from discord import app_commands
from clashopt.io import load_all
from clashopt.score import score

DATA_DIR = os.getenv(
    "CLASHOPT_DATA_DIR",
    r"C:\Users\heint\OneDrive\Documents\CodesNStuffz\clashTeam\data"
)

ctx_data = load_all(DATA_DIR)

def parse(s: str):
    return [x.strip() for x in s.replace(",", " ").split() if x.strip()]

def to_slots(champs: list[str]):
    return [{"champ": c, "comfort": 0, "role_fit": 0} for c in champs]

def g(d, *keys, default=0):
    for k in keys:
        if k in d:
            return d[k]
    return default

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "compare" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="compare", description="Compare two comps.", guild=guild)
    async def compare_cmd(interaction: discord.Interaction, comp1: str, comp2: str, enemy: str = None):
        t1 = parse(comp1)
        t2 = parse(comp2)
        e = parse(enemy) if enemy else []

        if len(t1) != 5 or len(t2) != 5:
            await interaction.response.send_message("Need 5 champs per comp.", ephemeral=True)
            return

        if enemy and len(e) != 5:
            await interaction.response.send_message("Enemy must have 5 champs.", ephemeral=True)
            return

        r1 = score(ctx_data, to_slots(t1), e if e else None)
        r2 = score(ctx_data, to_slots(t2), e if e else None)

        s1 = g(r1, "score")
        s2 = g(r2, "score")
        winner = "Comp 1" if s1 > s2 else "Comp 2" if s2 > s1 else "Tie"

        embed = discord.Embed(title="Comparison", color=0x9B59B6)
        embed.add_field(name="Comp 1", value=", ".join(t1), inline=False)
        embed.add_field(name="Comp 1 Score", value=f"{s1:.2f}", inline=True)
        embed.add_field(name="Comp 1 Wincon", value=str(g(r1, "wincon", "win_condition", default="unknown")), inline=True)

        embed.add_field(name="Comp 2", value=", ".join(t2), inline=False)
        embed.add_field(name="Comp 2 Score", value=f"{s2:.2f}", inline=True)
        embed.add_field(name="Comp 2 Wincon", value=str(g(r2, "wincon", "win_condition", default="unknown")), inline=True)

        if e:
            embed.add_field(name="Enemy", value=", ".join(e), inline=False)

        embed.add_field(name="Winner", value=winner, inline=True)
        embed.add_field(name="Gap", value=f"{abs(s1 - s2):.2f}", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=False)