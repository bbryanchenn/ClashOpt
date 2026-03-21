import discord
from discord import app_commands

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "help" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="help", description="Show command usage information.", guild=guild)
    async def help_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Commands",
            description="Available slash commands",
            color=discord.Color.blue()
        )

        for cmd in tree.get_commands(guild=guild):
            embed.add_field(
                name=f"/{cmd.name}",
                value=cmd.description or "No description",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)