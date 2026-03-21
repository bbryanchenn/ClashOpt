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


def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "why" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="why", description="Explain why a comp scored the way it did.", guild=guild)
    @app_commands.describe(
        comp="Your 5 champs, comma or space separated",
        enemy="Optional enemy 5 champs"
    )
    async def why_cmd(interaction: discord.Interaction, comp: str, enemy: str | None = None):
        team = parse(comp)
        enemy_team = parse(enemy) if enemy else []

        if len(team) != 5:
            await interaction.response.send_message("Need exactly 5 champs.", ephemeral=True)
            return

        if enemy and len(enemy_team) != 5:
            await interaction.response.send_message("Enemy comp must have exactly 5 champs.", ephemeral=True)
            return

        r = score(ctx_data, to_slots(team), enemy_team if enemy_team else None)

        if r.get("score") == float("-inf"):
            await interaction.response.send_message("That comp fails a draft constraint.", ephemeral=True)
            return

        positives = []
        negatives = []

        if r.get("synergy", 0) > 0:
            positives.append(f"Synergy: {r['synergy']:.2f}")
        if r.get("combo", 0) > 0:
            positives.append(f"Combo bonus: {r['combo']:.2f}")
        if r.get("draft_safety", 0) > 0:
            positives.append(f"Draft safety: {r['draft_safety']:.2f}")
        if r.get("damage_profile", 0) > 0:
            positives.append(f"Damage profile: {r['damage_profile']:.2f}")
        if r.get("flex", 0) > 0:
            positives.append(f"Flex: {r['flex']:.2f}")
        if r.get("patch", 0) > 0:
            positives.append(f"Patch score: {r['patch']:.2f}")

        if r.get("counter_risk", 0) > 0:
            negatives.append(f"Counter risk: {r['counter_risk']:.2f}")
        if r.get("execution_risk", 0) > 0:
            negatives.append(f"Execution risk: {r['execution_risk']:.2f}")
        if r.get("comfort", 0) == 0:
            negatives.append("Comfort not provided")
        if r.get("role_fit", 0) == 0:
            negatives.append("Role fit not provided")

        embed = discord.Embed(
            title="Why This Comp",
            description=", ".join(team),
            color=0x3498DB
        )

        if enemy_team:
            embed.add_field(name="Enemy", value=", ".join(enemy_team), inline=False)

        embed.add_field(name="Score", value=f"{r['score']:.2f}", inline=True)
        embed.add_field(name="Wincon", value=r.get("wincon", "none"), inline=True)
        embed.add_field(name="Tags", value=", ".join(r.get("tags", [])) or "None", inline=False)

        embed.add_field(
            name="Good",
            value="\n".join(positives) if positives else "No major positives found",
            inline=False
        )

        embed.add_field(
            name="Bad",
            value="\n".join(negatives) if negatives else "No major negatives found",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)