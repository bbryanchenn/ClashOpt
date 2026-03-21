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

def g(d, *k, default=0):
    for x in k:
        if x in d:
            return d[x]
    return default

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "draft" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="draft", description="Analyze a team comp.", guild=guild)
    async def draft_cmd(interaction: discord.Interaction, ally: str, enemy: str):
        A = parse(ally)
        E = parse(enemy)

        if len(A) != 5 or len(E) != 5:
            await interaction.response.send_message("Need 5 champs each.", ephemeral=True)
            return

        r = score(ctx_data, to_slots(A), E)

        embed = discord.Embed(title="Draft Analysis", color=0x00BFFF)
        embed.add_field(name="Ally", value=", ".join(A), inline=False)
        embed.add_field(name="Enemy", value=", ".join(E), inline=False)
        embed.add_field(name="Score", value=f"{g(r, 'score'):.2f}", inline=True)
        embed.add_field(name="Wincon", value=str(g(r, 'wincon', default='unknown')), inline=True)
        embed.add_field(name="Synergy", value=f"{g(r, 'synergy', 'syn'):.2f}", inline=True)
        embed.add_field(name="Counter Risk", value=f"{g(r, 'counter_risk', 'ctr'):.2f}", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=False)