from pathlib import Path
from clashopt.io import load_all
from clashopt.score import score
from clashopt.validate import validate

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

KT = ["K'Sante", "Sejuani", "Taliyah", "Xayah", "Rakan"]
T1 = ["Aatrox", "Vi", "Syndra", "Kai'Sa", "Nautilus"]

def slots(champs):
    roles = ["top", "jungle", "mid", "adc", "support"]
    return [{"role": r, "champ": c, "comfort": 8, "wr": 0.56, "games": 120} for r, c in zip(roles, champs)]

def main():
    ctx = load_all(str(DATA_DIR))
    validate(ctx)

    r = score(ctx, slots(T1), enemy=KT)

    print("ENEMY:", ", ".join(KT))
    print("T1:", ", ".join(T1))
    print(f"SCORE={r['score']:.2f} wincon={r['wincon']} comfort={r['comfort']:.2f} syn={r['synergy']:.2f} ctr={r['counter_risk']:.2f}")

if __name__ == "__main__":
    main()
