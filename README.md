# ClashOpt 

This is a software that optimizes a League of Legends team composition for Clash tournaments. It helps players select the best champions and roles to maximize their chances of winning based on various factors such as team synergy, opponent analysis, and meta trends.

I also implemented a discord bot that allows users to interact with the ClashOpt software directly from a Discord server. The bot can provide team composition suggestions, analyze matchups, and offer tips for improving team synergy. However, a standalone CLI-based version of the software is also available for users who prefers to customize their experience without relying on Discord.

## New Year Update Note

As of March 2026, I have added a web application that allows users to input their team compositions and receive real-time analysis and suggestions. The web app provides a user-friendly interface for players to optimize their team compositions and improve their chances of winning in Clash tournaments. Given the complexity of the software, I have planned to release the web app as the main interface for ClashOpt, while maintaining the CLI and Discord bot versions for users who prefer those platforms and for development purposes. The web app will be the primary focus for future updates and improvements, while the CLI and Discord bot will receive maintenance updates to ensure compatibility with the latest champion data and meta trends. 

## New Year Update - March 2026

### ![new update](https://img.shields.io/badge/NEW-activated) Unified Data Engine
ClashOpt now uses a unified champion dataset (`champion_full.json`) that merges:

- Champion metadata
- Synergy pairs
- Counter relationships
- Combo definitions

The system maintains compatibility with legacy structures (`synergy`, `counters`) with internal reconstruction.

### ![new update](https://img.shields.io/badge/NEW-activated) Web App Integration

ClashOpt now includes a web-based draft analyzer.

#### Features
- Input both team comps (Blue vs Red)
- Real-time draft comparison
- Outputs:
     - Win condition
     - Synergy score
     - Counter risk
     - Draft summary

### ![new update](https://img.shields.io/badge/NEW-activated) Discord Updates
- Added multiple commands: `/help`, `/wincon`, `/draft`, `/compare`
- Improved error handling and user feedback


# Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Web App Usage](#web-app-usage)
- [CLI Usage](#cli-usage-how-to-use-clashopt)
- [Discord Bot Usage](#discord-bot-usage)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Notes](#notes)


# Requirements

- Python 3.8

## Dependencies
- disord.py
- requests
- httpx
- python-dotenv

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

---

# Web App Usage

To run the ClashComp web application, you need to start both the backend API and the frontend. Note that both the backend and frontend need to be running simultaneously for the web app to function properly.

## Backend
For the backend, from the root directory (`clashopt/`), run:
```
uvicorn app.api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. 

## Frontend
For the frontend, navigate to `web/` and run:
```
cd web
npm run dev
```
Then open your browser and go to `http://localhost:3000` to access the ClashOpt web application.

## Architecture
```
Frontend (Next.js)
    ↓
FastAPI Backend
    ↓
ClashOpt Core Engine
```
## API Endpoints

`POST /compare`: Compares two team compositions and returns a detailed analysis including win conditions, synergy scores, and counter risks.


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

- `/wincon`: Returns the score, synergy, and counter risk of a specific team comp.

- 

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
- `/wincon <champ1> <champ2> <champ3> <champ4> <champ5>`: Analyzes the win conditions of a specific team composition.
- `/compare <champ1> <champ2> <champ3> <champ4>`: Compares two team compositions and provides insights on their strengths and weaknesses.
- `/draft <enemy> <topk> <show>`: Simulates a draft scenario and suggests optimal picks and bans.
- `/draftsim <enemy> <topk> <show>`: Simulates a draft scenario with more detailed analysis and suggestions.
- `/help`: Provides information on its commands.
- `/why`: Explains the reasoning behind the bot's suggestions for a given team composition.
- `/recent <name#tag>`: Shows the last 5 matches of a player.

# Project Structure

```
clashTeam/
├─ app/
│ └─ web/
│   └─ main.py
├─ data/
│ ├─ team.json
│ ├─ champ_db.json
│ ├─ synergy.json
│ ├─ counters.json
| ├─ champion_full.json
│ └─ draft_rules.json
├─ src/
│ └─ clashopt/
│   ├─ __init__.py
│   ├─ bans.py
│   ├─ cli.py
│   ├─ io.py
│   ├─ model.py
│   ├─ names.py
│   ├─ report.py
│   ├─ score.py
│   ├─ search.py
│   └─ validate.py
├─ discord/
│ ├─ bot.py
│ ├─ run.bat
│ ├─ requirements.txt
│ ├─ .env
│ └─ commands/
│   ├─ init.py
│   ├─ admin.py
│   ├─ best.py
│   ├─ bans.py
│   ├─ compare.py
│   ├─ draft.py
│   ├─ draftsim.py
│   ├─ help.py
│   ├─ resilient.py
│   ├─ pivot.py
│   ├─ ping.py
│   ├─ say.py
│   ├─ why.py
│   ├─ wincon.py
│   └─ recent.py
├─ web/
│ ├─ src/
| ├─ components/
| └─ app/
│   └─ page.tsx
└─ pyproject.toml
```

# Notes

- Ensure you have the necessary permissions to add the bot to your Discord server.
- Keep all your API keys and tokens secure and do not share them publicly.
- Regularly update the champion and team data to stay current with the latest meta trends.
- For any issues or feature requests, please open an issue in the repository.