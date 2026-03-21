import discord
from discord import app_commands

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "say" for c in tree.get_commands(guild=guild)):
        return
    @tree.command(name="say", description="Repeats after you", guild=guild)
    async def say_cmd(interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message, ephemeral=False)