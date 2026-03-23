# Architecture

## High-Level Components

- **Data layer** (`data/`): champion metadata, synergy, counters, draft rules.
- **Core engine** (`src/clashopt/`): scoring, validation, reporting, search.
- **Discord interface** (`discord/`): slash-command entrypoint and command modules.
- **Web interface** (`web/`): Next.js frontend for interactive draft analysis.

## Data Flow

1. User submits team compositions.
2. Input normalization + validation.
3. Core model computes score/synergy/counter risk.
4. Interface layer renders response (CLI/Discord/Web).
