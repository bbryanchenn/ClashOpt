import importlib
import discord
from discord import app_commands

from . import DEFAULT_MODULES
from . import load_commands

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "resync" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(
        name="resync",
        description="Reload command files + resync slash commands (admin only).",
        guild=guild
    )
    async def resync_cmd(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        loaded, failed = [], []

        for name in DEFAULT_MODULES:
            mod_name = f"commands.{name}"
            try:
                m = importlib.import_module(mod_name)
                importlib.reload(m)
                loaded.append(name)
            except Exception as e:
                failed.append((name, repr(e)))

        try:
            if guild:
                tree.clear_commands(guild=guild)
                await tree.sync(guild=guild)
                from commands import load_commands
                load_commands(tree, bot, guild=guild)
                await tree.sync(guild=guild)
            else:
                await tree.sync()
        except Exception as e:
            await interaction.followup.send(
                f"✅ Reloaded: {', '.join(loaded)}\n❌ Sync failed: {repr(e)}",
                ephemeral=True
            )
            return

        msg = f"✅ Reloaded: {', '.join(loaded)}\n✅ Synced commands"
        if failed:
            msg += "\n\n⚠️ Failed:\n" + "\n".join([f"- {n}: {err}" for n, err in failed])

        await interaction.followup.send(msg, ephemeral=True)
