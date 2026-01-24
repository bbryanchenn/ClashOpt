import asyncio, json, re
from playwright.async_api import async_playwright

XPATH = "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div/div[1]/div[1]"

PAIRS = [
    ("reksai", "Zac", "jungle"),
    ("volibear", "Zac", "jungle"),
    ("kindred", "Zac", "jungle")

]

def url_for(a: str, b: str, role: str) -> str:
    return f"https://u.gg/lol/champions/{a}/build/{role}?opp={b}&rank=overall"

def parse_number(text: str):
    if not text:
        return None
    t = text.strip().replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return round(float(m.group(0)) / 100, 2) if m else None

async def scrape_pair(page, a: str, b: str, role: str):
    await page.goto(url_for(a, b, role), wait_until="domcontentloaded")
    el = page.locator(f"xpath={XPATH}")
    await el.wait_for(state="visible", timeout=15000)
    raw = await el.inner_text()
    return {"a": a, "b": b, "role": role, "value": parse_number(raw)}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # set True to hide window
        context = await browser.new_context()
        page = await context.new_page()

        out = []
        for a, b, role in PAIRS:
            try:
                out.append(await scrape_pair(page, a, b, role))
            except Exception:
                out.append({"a": a, "b": b, "value": None})

        await browser.close()
        print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
