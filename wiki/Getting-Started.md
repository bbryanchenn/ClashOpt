# Getting Started

## Prerequisites

- Python 3.10+
- Node.js 20+ (for `web/`)
- Optional: Discord bot token + Riot API key for bot features

## Setup

1. Clone the repository.
2. Install backend/core dependencies.
3. Install Discord dependencies (if using bot).
4. Install web dependencies (if using web UI).
5. Create `discord/.env` and set required values.

## Minimal Run Commands

### Discord Bot

```bash
cd discord
python bot.py
```

### Web App

```bash
cd web
npm install
npm run dev
```

## First Validation

- Try a known sample draft in the web page.
- In Discord, run `/help` then `/wincon` and `/compare`.
