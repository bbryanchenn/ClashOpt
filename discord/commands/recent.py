import discord
from discord import app_commands
import aiohttp, os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

ROUTING = {
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    "kr": "asia",
    "jp1": "asia",
    "oc1": "sea",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
}

ROLE_EMOJIS = {
    "TOP": 1484795247820144770,
    "JUNGLE": 1484795126059630602,
    "MIDDLE": 1484795186012749875,
    "BOTTOM": 1484795279197605938,
    "UTILITY": 1484795220666089642,
}

ROLE_LABELS = {
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "MIDDLE": "Mid",
    "BOTTOM": "ADC",
    "UTILITY": "Support",
    "": "Unknown",
}

async def riot_get(session: aiohttp.ClientSession, url: str):
    async with session.get(url, headers={"X-Riot-Token": RIOT_API_KEY}) as r:
        if r.status != 200:
            text = await r.text()
            raise RuntimeError(f"Riot API {r.status}: {text[:200]}")
        return await r.json()

def kda_str(k, d, a):
    return f"{k}/{d}/{a} ({((k + a) / max(1, d)):.2f})"

def normalize_role(role: str) -> str:
    role = (role or "").upper()
    aliases = {
        "MID": "MIDDLE",
        "ADC": "BOTTOM",
        "BOT": "BOTTOM",
        "SUPPORT": "UTILITY",
        "SUP": "UTILITY",
    }
    return aliases.get(role, role)

def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "recent" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="recent", description="Show recent LoL match stats.", guild=guild)
    async def recent_cmd(
        interaction: discord.Interaction,
        summoner: str,
        tag: str,
        platform: str = "na1",
        count: int = 5,
    ):
        platform = platform.lower()
        if platform not in ROUTING:
            return await interaction.response.send_message(
                "Invalid platform. Use na1/euw1/kr/etc.", ephemeral=False
            )

        if not RIOT_API_KEY:
            return await interaction.response.send_message(
                "Missing RIOT_API_KEY env var.", ephemeral=False
            )

        count = max(1, min(count, 5))
        routing = ROUTING[platform]

        await interaction.response.defer(thinking=True)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            acct = await riot_get(
                session,
                f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
                f"{aiohttp.helpers.quote(summoner)}/{aiohttp.helpers.quote(tag)}",
            )
            puuid = acct["puuid"]

            match_ids = await riot_get(
                session,
                f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/"
                f"{puuid}/ids?start=0&count={count}",
            )

            embeds = []
            for mid in match_ids:
                match = await riot_get(
                    session,
                    f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{mid}",
                )
                info = match["info"]
                p = next(x for x in info["participants"] if x["puuid"] == puuid)

                win = "✅ Win" if p["win"] else "❌ Loss"
                champ = p["championName"]

                raw_role = p.get("teamPosition") or p.get("individualPosition") or ""
                role_key = normalize_role(raw_role)
                role_name = ROLE_LABELS.get(role_key, raw_role.title() if raw_role else "Unknown")

                emoji_id = ROLE_EMOJIS.get(role_key)
                emoji = bot.get_emoji(emoji_id) if emoji_id else None
                emoji_str = str(emoji) if emoji else ""

                k, d, a = p["kills"], p["deaths"], p["assists"]
                cs = p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0)
                gold = p["goldEarned"]
                dmg = p["totalDamageDealtToChampions"]
                mins = info["gameDuration"] / 60

                embeds.append(
                    discord.Embed(
                        title=f"{win} — {emoji_str} {champ}",
                        description=(
                            f"**KDA:** {kda_str(k,d,a)}\n"
                            f"**CS:** {cs} ({cs/max(1,mins):.1f}/min)\n"
                            f"**Gold:** {gold:,} | **Dmg:** {dmg:,}\n"
                            f"**Duration:** {mins:.1f} min"
                        ),
                    )
                )

            header = discord.Embed(
                title=f"Recent games — {acct['gameName']}#{acct['tagLine']}",
                description=f"Platform: `{platform}` • Showing last {len(embeds)} matches",
            )

            await interaction.followup.send(embeds=[header, *embeds])