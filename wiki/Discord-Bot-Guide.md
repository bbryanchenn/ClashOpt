# Discord Bot Guide

## Environment Variables

Typical values in `discord/.env`:

- `DISCORD_TOKEN`
- `DATA_DIR`
- `CHANNEL_ID`
- `TEST_CHANNEL_ID`
- `GUILD_ID`
- `RIOT_API_KEY`

## Common Commands

- `/best`
- `/bans`
- `/resilient`
- `/pivot`
- `/wincon`
- `/compare`
- `/draft`
- `/draftsim`
- `/recent`

## Notes

- Use `GUILD_ID` while iterating on slash commands for fast guild sync.
- `/recent` requires a working Riot API key.
