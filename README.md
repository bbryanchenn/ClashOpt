# ClashOpt 

This is a software that optimizes a League of Legends team composition for Clash tournaments. It helps players select the best champions and roles to maximize their chances of winning based on various factors such as team synergy, opponent analysis, and meta trends.

I also implemented a discord bot that allows users to interact with the ClashOpt software directly from a Discord server. The bot can provide team composition suggestions, analyze matchups, and offer tips for improving team synergy. However, a standalone CLI-based version of the software is also available for users who prefers to customize their experience without relying on Discord.

# Requirements

- Python 3.8

## Dependencies
- disord.py
- requests
- httpx

# Setup

1. Clone the repository:
```
git clone
```

2. Navigate to the project directory and install the required dependencies for standalone CLI version and discord bot:
CLI/Core:
```
pip install -r src/clashopt/requirements.txt
```
Python:
```
pip install -r discord/requirements.txt
```

3. For the Discord bot, create a `.env` file in the `discord/` directory and add your Discord bot token:
```
DISCORD_TOKEN=
DATA_DIR=./data
CHANNEL_ID=
TEST_CHANNEL_ID=
GUILD_ID=
RIOT_API_KEY=
```

# CLI Usage (How to use ClashOpt)

You always run:
```
clashopt <command> [flags]
```

## Available Commands

- `best`: Finds the best 5-man comp from your team pools using your scoring model.
> Useful flags: 
> `--enemy`: Adds enemy champs into the calculation (counters)
> `--topk`: How many comps it generates internally before ranking
> `--show`: How many of the best comps to show

- `bans`: Simulates bans based on a ban model (like “they’ll ban your best champs”).
> Useful flags:
> `--model`: Which ban model to use (best, robbery_best_player, one_per_role)
> `--seed`: Seed for random number generator (for reproducibility)

- `resilient`: Finds comps that are harder to ban out
> Useful flags:
> `--scenarios`: Number of random ban scenarios to simulate
> `--model`: Which ban model to use (best, robbery_best_player, one_per_role)
> `--seed`: Seed for random number generator (for reproducibility)

- `pivot`: This is the “draft survival” command: gives you a good base comp that simulates bans and shows the best pivot picks after bans hit
> Useful flags:
> `--model`: Which ban model to use (best, robbery_best_player)
> `--seed`: Seed for random number generator (for reproducibility)
> `--enemy`: Adds enemy champs into the calculation (counters)

### Global Flags
- `--data`: Path to the data directory (default: ./data, directory to /data )

# Discord Bot Usage

To run the Discord bot, navigate to the `discord/` directory and execute the `bot.py` script:
```
python bot.py
```
This will start the bot and connect it to your Discord server. You can then use the available commands to interact with the ClashOpt software.

## Commands

- `/best <enemy> <topk> <show> <ban_model>`: Suggests the best team composition based on the current meta and team synergy.
- `/bans <seed> <model>`: Recommends champions to ban based on the opponent's team composition.
- `/resilient <scenarios> <topk> <show> <model>`: Suggests a resilient team composition that can withstand various strategies.\
- `/pivot <seed> <topk> <show> <model>`: Suggests champions to pivot around based on the current team composition.
- `/resync`: Resynchronizes the bot's data with the latest champion and team information.

# Project Structure

```
clashTeam/
├─ data/
│ ├─ team.json
│ ├─ champ_db.json
│ ├─ synergy.json
│ ├─ counters.json
│ └─ draft_rules.json
├─ src/
│ └─ clashopt/
├─ discord/
│ ├─ bot.py
│ ├─ run.bat
│ ├─ requirements.txt
│ ├─ .env
│ └─ commands/
│ ├─ init.py
│ ├─ admin.py
│ ├─ best.py
│ ├─ bans.py
│ ├─ resilient.py
│ ├─ pivot.py
│ ├─ ping.py
│ ├─ say.py
│ └─ recent.py
└─ pyproject.toml
```

# Notes

- Ensure you have the necessary permissions to add the bot to your Discord server.
- Keep all your API keys and tokens secure and do not share them publicly.
- Regularly update the champion and team data to stay current with the latest meta trends.
- For any issues or feature requests, please open an issue in the repository.