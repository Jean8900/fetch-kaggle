"""Lecture des onglets publics d'une compétition Kaggle (Playwright, sans token).

Les pages Kaggle sont rendues en JavaScript : un simple `curl` ne renvoie qu'une coquille.
Chaque onglet produit un fichier texte, une capture d'écran, et un index.json récapitulatif.
Un onglet qui échoue n'interrompt pas les autres.
"""
import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

TABS = {
    "overview": "",
    "data": "/data",
    "code": "/code",
    "discussion": "/discussion",
    "rules": "/rules",
}
NOT_FOUND_MARKERS = ("we can't find that page", "page not found")
NOTEBOOK_HREF = re.compile(r"^/code/([^/]+)/([^/?#]+)")  # ex. /code/owner/slug/comments


async def _notebooks(page) -> list:
    hrefs = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    seen, found = set(), []
    for href in hrefs:
        m = NOTEBOOK_HREF.match(href or "")
        if m and m.group(0) not in seen:
            seen.add(m.group(0))
            found.append({"ref": f"{m.group(1)}/{m.group(2)}",
                          "url": f"https://www.kaggle.com/code/{m.group(1)}/{m.group(2)}"})
    return found


async def fetch_tabs(slug: str, out_dir: Path, tabs=None, wait_ms: int = 6000) -> dict:
    tabs = tabs or list(TABS)
    base = f"https://www.kaggle.com/competitions/{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(locale="en-US")).new_page()
        for name in tabs:
            try:
                await page.goto(base + TABS[name], wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(wait_ms)
                text = await page.inner_text("body")
                (out_dir / f"{name}.txt").write_text(text, encoding="utf-8")
                await page.screenshot(path=str(out_dir / f"{name}.png"))
                entry = {"url": page.url, "chars": len(text), "status": "ok"}
                if any(marker in text.lower() for marker in NOT_FOUND_MARKERS):
                    entry["status"] = "not_found"
                if name == "code":
                    entry["notebooks"] = await _notebooks(page)
                result[name] = entry
                print(f"[{name}] {entry['status']} ({entry['chars']} car.)")
            except Exception as exc:  # une erreur sur un onglet ne stoppe pas les autres
                result[name] = {"status": "error", "error": str(exc)[:300]}
                print(f"[{name}] erreur : {exc}")
        await browser.close()
    (out_dir / "index.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def fetch_tabs_sync(slug: str, out_dir: Path, tabs=None) -> dict:
    return asyncio.run(fetch_tabs(slug, out_dir, tabs))
