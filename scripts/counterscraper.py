import asyncio, json, re
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

CHAMPS = [ 
   
  ]

CONCURRENCY = 6
HEADLESS = True

NAME_XPATHS = [
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[1]/div[2]/div[1]",
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[2]/div[2]/div[1]",
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[3]/div[2]/div[1]",
]
WR_XPATHS = [
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[1]/div[3]/div[1]",
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[2]/div[3]/div[1]",
    "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/a[3]/div[3]/div[1]",
]

_wr_re = re.compile(r"-?\d+(?:[.,]\d+)?")

def parse_wr(text: str):
    if not text:
        return None
    m = _wr_re.search(text)
    if not m:
        return None
    return round(float(m.group(0).replace(",", ".")) / 100.0, 4)

def url_for(champ: str) -> str:
    return f"https://u.gg/lol/champions/{champ}/counter"

async def block(route):
    rt = route.request.resource_type
    if rt in ("image", "media", "font", "stylesheet"):
        await route.abort()
    else:
        await route.continue_()

async def grab(page, xpath: str, timeout=6000):
    loc = page.locator(f"xpath={xpath}").first
    await loc.wait_for(state="attached", timeout=timeout)
    return (await loc.inner_text()).strip()

async def scrape_champ(page, champ: str):
    url = url_for(champ)
    last_err = None

    for _ in range(2):  # 1 retry
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)

            # KEY: wait only for the first expected element, not "networkidle"
            await page.locator(f"xpath={NAME_XPATHS[0]}").wait_for(state="visible", timeout=12000)

            out = []
            # read in tight loop (no per-locator waits now)
            for nx, wx in zip(NAME_XPATHS, WR_XPATHS):
                a = (await page.locator(f"xpath={nx}").first.inner_text()).strip()
                wr_raw = (await page.locator(f"xpath={wx}").first.inner_text()).strip()
                v = parse_wr(wr_raw)
                if a and v is not None:
                    out.append({"a": a, "b": champ.capitalize(), "value": round(v, 2)})
            return out
        except Exception as e:
            last_err = e
            try:
                await page.reload(wait_until="domcontentloaded", timeout=15000)
            except Exception:
                pass

    raise last_err

async def worker(q: asyncio.Queue, ctx, results: list):
    page = await ctx.new_page()
    while True:
        champ = await q.get()
        if champ is None:
            q.task_done()
            break
        try:
            results.extend(await scrape_champ(page, champ))
        except PWTimeout:
            pass
        except Exception:
            pass
        q.task_done()
    await page.close()

async def main():
    champs = [c.strip().lower() for c in CHAMPS if c.strip()]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 720})
        await ctx.route("**/*", block)

        # warm-up (loads JS bundles once)
        warm = await ctx.new_page()
        await warm.goto(url_for(champs[0]), wait_until="domcontentloaded", timeout=15000)
        await warm.close()

        q = asyncio.Queue()
        for c in champs:
            q.put_nowait(c)

        results = []
        n = min(CONCURRENCY, len(champs))
        tasks = [asyncio.create_task(worker(q, ctx, results)) for _ in range(n)]
        for _ in range(n):
            q.put_nowait(None)

        await q.join()
        await asyncio.gather(*tasks)

        await ctx.close()
        await browser.close()

        print(json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
