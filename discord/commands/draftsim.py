import os
import discord
from discord import app_commands

from clashopt.io import load_all
from clashopt.search import resilient_comps

DATA_DIR = os.getenv(
    "CLASHOPT_DATA_DIR",
    r"C:\Users\heint\OneDrive\Documents\CodesNStuffz\clashTeam\data"
)

ctx_data = load_all(DATA_DIR)


def fmt_comp(comp):
    return ", ".join(x["champ"] for x in comp)


def setup(tree: app_commands.CommandTree, bot, guild=None):
    if any(c.name == "draftsim" for c in tree.get_commands(guild=guild)):
        return

    @tree.command(name="draftsim", description="Simulate resilient comps across ban scenarios.", guild=guild)
    @app_commands.describe(
        topk="How many candidates per role to search",
        show="How many comps to display",
        ban_model="Ban model from your draft_rules/team logic",
        scenarios="How many simulated ban scenarios to run"
    )
    async def draftsim_cmd(
        interaction: discord.Interaction,
        topk: app_commands.Range[int, 1, 20] = 8,
        show: app_commands.Range[int, 1, 10] = 5,
        ban_model: str = "default",
        scenarios: app_commands.Range[int, 1, 50] = 10
    ):
        results = resilient_comps(
            ctx_data,
            topk=topk,
            show=show,
            ban_model=ban_model,
            scenarios=scenarios
        )

        if not results:
            await interaction.response.send_message("No resilient comps found.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Draft Simulation",
            description=f"topk={topk} • scenarios={scenarios} • model={ban_model}",
            color=0xF39C12
        )

        for i, r in enumerate(results, 1):
            embed.add_field(
                name=f"#{i}  avg={r['avg']:.2f}  worst={r['worst']:.2f}  viable={r['viable']}",
                value=fmt_comp(r["comp"]),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=False)