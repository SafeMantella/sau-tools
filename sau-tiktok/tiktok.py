"""sau-tiktok: o SAU não tem `sau tiktok`; isto liga o TiktokVideo dele a um CLI.
Uso: sau-tiktok login | upload-video --file v.mp4 --title T [--tags a,b] [--schedule "AAAA-MM-DD HH:MM"]"""
import argparse
import asyncio
import sys
from pathlib import Path

SAU = Path(__file__).resolve().parents[3] / "social-auto-upload"  # clone fica em ferramentas/_repos/sau-tools/: sobe até ferramentas/
sys.path.insert(0, str(SAU))
import patchright.async_api as _pw  # noqa: E402

# o uploader do SAU importa `playwright`, que não está instalado (só patchright)
sys.modules.setdefault("playwright", sys.modules["patchright"])
sys.modules.setdefault("playwright.async_api", _pw)

from sau_commands.arguments import existing_file_path, parse_tags, resolve_account_file, schedule_value  # noqa: E402
from uploader.tk_uploader.main_chrome import TiktokVideo  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def logged_in(cookies):
    return any(c["name"] == "sessionid" and "tiktok.com" in c["domain"] for c in cookies)


def parser():
    p = argparse.ArgumentParser(prog="sau-tiktok")
    p.add_argument("--account", default="pedro")
    s = p.add_subparsers(dest="action", required=True)
    s.add_parser("login")
    u = s.add_parser("upload-video")
    u.add_argument("--file", required=True, type=existing_file_path)
    u.add_argument("--title", required=True)
    u.add_argument("--tags", default="")
    u.add_argument("--schedule", type=schedule_value, default=0)
    return p


class Video(TiktokVideo):
    async def add_title_tags(self, page):
        # no Mac Control+A só vai ao início da linha: sobrava o nome do arquivo na legenda. Cmd+A seleciona tudo.
        press = page.keyboard.press
        page.keyboard.press = lambda k: press("Meta+A" if k == "Control+A" else k)
        await super().add_title_tags(page)


def video(a):
    v = Video(a.title, a.file, parse_tags(a.tags), a.schedule, resolve_account_file("tiktok", a.account))
    v.headless, v.local_executable_path = False, CHROME  # TikTok recusa headless
    return v


async def login(account_file):
    async with _pw.async_playwright() as p:
        browser = await p.chromium.launch(headless=False, executable_path=CHROME)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto("https://www.tiktok.com/login?lang=en")
        for _ in range(600):  # até 10 min pro login manual
            if logged_in(await ctx.cookies()):
                break
            await asyncio.sleep(1)
        else:
            sys.exit("timeout: login não concluído")
        await ctx.storage_state(path=str(account_file))
        print(f"sessão salva: {account_file}")


def main():
    a = parser().parse_args()
    if a.action == "login":
        asyncio.run(login(resolve_account_file("tiktok", a.account)))
    else:  # ponytail: o uploader do SAU tem `while True`; 15 min de teto evita travar pra sempre
        asyncio.run(asyncio.wait_for(video(a).main(), 900))


if __name__ == "__main__":
    main()
