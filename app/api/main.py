from pathlib import Path
import difflib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from clashopt.io import load_all
from clashopt.names import build_name_map, canon
from clashopt.score import compare_drafts

app = FastAPI()

ROOT = Path(__file__).resolve().parents[2]
ctx = load_all(str(ROOT / "data"))
name_map = build_name_map(ctx.champ_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompareRequest(BaseModel):
    blue: list[str]
    red: list[str]

def normalize_team(team: list[str]) -> list[str]:
    out = []
    for champ in team:
        try:
            out.append(canon(champ, name_map))
        except KeyError:
            suggestions = difflib.get_close_matches(champ, name_map.keys(), n=1)
            if suggestions:
                suggestion = name_map[suggestions[0]]
                msg = f"Invalid champion: {champ}. Did you mean {suggestion}?"
            else:
                msg = f"Invalid champion: {champ}"

            raise HTTPException(status_code=400, detail=msg)
    return out

@app.post("/compare")
def compare(req: CompareRequest):
    blue = normalize_team(req.blue)
    red = normalize_team(req.red)

    if len(blue) != 5 or len(red) != 5:
        raise HTTPException(status_code=400, detail="Each team must have exactly 5 champions")

    all_picks = blue + red
    if len(set(all_picks)) != len(all_picks):
        raise HTTPException(status_code=400, detail="Duplicate champions are not allowed across both teams")

    return compare_drafts(ctx, blue, red)