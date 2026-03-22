import os
import discord
import aiohttp
from discord import app_commands

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
REGION = "na1"
ACCOUNT_REGION = "americas"

async def get_json(session, url):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"{resp.status}: {text}")
        return await resp.json()

async def get_latest_ddragon_version(session):
    async with session.get("https://ddragon.leagueoflegends.com/api/versions.json") as resp:
        data = await resp.json()
        return data[0]

async def get_champion_map(session, version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    async with session.get(url) as resp:
        data = await resp.json()
        return {int(v["key"]): v["name"] for v in data["data"].values()}

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "mastery" for c in tree.get_commands()):
        return

    @tree.command(name="mastery", description="Show top 5 mastery for a Riot ID.", guild=guild)
    @app_commands.describe(
        username="Riot game name",
        tag_line="Riot tag"
    )
    async def mastery_cmd(interaction: discord.Interaction, username: str, tag_line: str):
        await interaction.response.defer(ephemeral=False)

        if not RIOT_API_KEY:
            await interaction.followup.send("Missing RIOT_API_KEY in environment.", ephemeral=False)
            return

        try:
            async with aiohttp.ClientSession() as session:
                account = await get_json(
                    session,
                    f"https://{ACCOUNT_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag_line}"
                )
                puuid = account["puuid"]

                mastery = await get_json(
                    session,
                    f"https://{REGION}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
                )

                if not mastery:
                    await interaction.followup.send("No mastery data found.", ephemeral=False)
                    return

                version = await get_latest_ddragon_version(session)
                champ_map = await get_champion_map(session, version)

                top5 = mastery[:5]
                lines = []
                for i, champ in enumerate(top5, 1):
                    champ_name = champ_map.get(champ["championId"], f"ID {champ['championId']}")
                    lines.append(
                        f"**{i}. {champ_name}**\n"
                        f"Level: {champ['championLevel']} | Points: {champ['championPoints']:,}"
                    )

                embed = discord.Embed(
                    title=f"Top 5 Mastery: {username}#{tag_line}",
                    description="\n\n".join(lines),
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Region: {REGION.upper()}")
                await interaction.followup.send(embed=embed, ephemeral=False)

        except Exception as e:
            await interaction.followup.send(f"Failed to fetch mastery: `{e}`", ephemeral=False)