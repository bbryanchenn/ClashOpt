import discord
from discord import app_commands
from commands import DEFAULT_MODULES

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "ping" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="ping", description="Check bot responsiveness.", guild=guild)
    async def ping_cmd(interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=False)