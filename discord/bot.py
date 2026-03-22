import os
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

from clashopt.io import load_all
from clashopt.validate import validate
from clashopt.names import build_name_map

from commands import load_commands

load_dotenv(Path(__file__).resolve().with_name(".env"))

BOT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", str((BOT_DIR.parent / "data").resolve()))).resolve()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
BOOT_CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

def guild_obj():
    return discord.Object(id=GUILD_ID) if GUILD_ID else None

class ClashBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.ctx = None
        self.nm = None

    async def setup_hook(self):
        self.ctx = load_all(str(DATA_DIR))
        validate(self.ctx)
        self.nm = build_name_map(self.ctx.champ_db)

        g = guild_obj()
        if g:
            # wipe GLOBAL commands too (one-time cleanup)
            self.tree.clear_commands(guild=None)
            await self.tree.sync()  # global delete (propagation can take a while)

            # wipe + re-add GUILD commands (instant)
            self.tree.clear_commands(guild=g)
            await self.tree.sync(guild=g)

            load_commands(self.tree, self, guild=g)
            await self.tree.sync(guild=g)
        else:
            # global reset is slow; avoid unless you really want it
            self.tree.clear_commands()
            await self.tree.sync()
            load_commands(self.tree, self, guild=None)
            await self.tree.sync()
            print("Reset & synced globally")


    async def on_ready(self):
        print(f"READY {self.user} ({self.user.id})")
        if not BOOT_CHANNEL_ID:
            return
        try:
            ch = await self.fetch_channel(BOOT_CHANNEL_ID)
            print("Faker is here to stay.")
            # await ch.send("erm ok")
            # await ch.send("In the midlane... The Unkillable Demon King... FAKERRRRRRRRR" )
            # await ch.send("https://tenor.com/view/faker-unkillable-demon-king-t1-t1fight-lol-gif-7065924072719595842")
        except Exception as e:
            print("Boot msg failed:", repr(e))

bot = ClashBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    msg = f"⚠️ `{type(error).__name__}`: {error}"
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass
    raise error

def main():
    if not TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN in discord/.env")
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
