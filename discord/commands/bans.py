import os
import discord
from discord import app_commands

from clashopt.bans import simulate_bans
from clashopt.names import canon

DEFAULT_MODEL = os.getenv("DEFAULT_BAN_MODEL", "robbery_best_player")



def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "bans" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="bans", description="Simulate bans using a ban model.", guild=guild)
    @app_commands.describe(model="Ban model name.", seed="Random seed.")
    async def bans_cmd(interaction: discord.Interaction, model: str = DEFAULT_MODEL, seed: int = 0):
        await interaction.response.defer(ephemeral=False)
        banned = simulate_bans(bot.ctx.team, bot.ctx.rules, model, seed=seed)
        banned = sorted({canon(b, bot.nm) for b in banned})
        await interaction.followup.send(f"**BANNED ({model})**: {', '.join(banned) if banned else '(none)'}", ephemeral=False)
