# discord/commands/__init__.py
import importlib
from pathlib import Path

_commands_dir = Path(__file__).resolve().parent
DEFAULT_MODULES = sorted(
    f.stem for f in _commands_dir.glob("*.py")
    if f.is_file() and f.stem != "__init__"
)

_loaded = False

def load_commands(tree, bot, guild=None):
    global _loaded
    if _loaded:
        return
    _loaded = True

    print("Loading command modules:", DEFAULT_MODULES)

    pkg = __package__  # "commands"
    for name in DEFAULT_MODULES:
        m = importlib.import_module(f"{pkg}.{name}")
        setup = getattr(m, "setup", None)
        if setup:
            setup(tree, bot, guild=guild)
