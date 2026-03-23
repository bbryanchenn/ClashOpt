# Troubleshooting

## Discord commands not showing

- Confirm bot invite includes `applications.commands` scope.
- Ensure `GUILD_ID` is set for quick command sync.
- Restart bot after command module changes.

## `/recent` fails

- Verify `RIOT_API_KEY` is present and valid.
- Check platform routing inputs (`na1`, `euw1`, `kr`, etc.).

## Web build fails on fonts

- In restricted environments, `next/font` may fail to fetch Google Fonts.
- Re-run build with network access or switch to local font fallback.

## Backend call errors

- Ensure API is running at `http://127.0.0.1:8000/compare`.
- Verify request payload has 5 valid champs per side.
