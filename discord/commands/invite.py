import discord
from discord import app_commands
from discord.utils import oauth_url

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "invite" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="invite", description="Get the bot invite link.", guild=guild)
    async def invite_cmd(interaction: discord.Interaction):
        perms = discord.Permissions(
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=True
        )

        invite_link = oauth_url(
            bot.user.id,
            permissions=perms,
            scopes=("bot", "applications.commands")
        )

        embed = discord.Embed(
            title="Invite ClashComp",
            description=f"[Click here to invite the bot]({invite_link})",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)