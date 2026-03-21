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

def g(d, *k, default=0):
    for x in k:
        if x in d:
            return d[x]
    return default

def to_slots(champs: list[str]):
    return [{"champ": c, "comfort": 0, "role_fit": 0} for c in champs]

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "wincon" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="wincon", description="Show win condition.", guild=guild)
    async def wincon_cmd(interaction: discord.Interaction, comp: str, enemy: str = None):
        T = parse(comp)
        E = parse(enemy) if enemy else []

        if len(T) != 5:
            await interaction.response.send_message("Need 5 champs.", ephemeral=True)
            return

        r = score(ctx_data, to_slots(T), E)

        embed = discord.Embed(title="Win Condition", color=0x2ecc71)
        embed.add_field(name="Team", value=", ".join(T), inline=False)

        if E:
            embed.add_field(name="Enemy", value=", ".join(E), inline=False)

        embed.add_field(name="Wincon", value=str(g(r,'wincon','win_condition','unknown')))
        embed.add_field(name="Score", value=f"{g(r,'score'):.2f}")
        embed.add_field(name="Synergy", value=f"{g(r,'synergy','syn'):.2f}")
        embed.add_field(name="Counter Risk", value=f"{g(r,'counter_risk','ctr'):.2f}")

        await interaction.response.send_message(embed=embed, ephemeral=False)