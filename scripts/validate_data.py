import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clashopt.io import load_all
from clashopt.validate import validate

if __name__ == "__main__":
    ctx = load_all(str(ROOT / "data"))
    for _module in ["champ_db", "team", "synergy", "counters", "patch"]:
        print(f"Validating {_module}")
    validate(ctx)
    print("ALL CLEAR - data validation passed!")
