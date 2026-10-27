#!/usr/bin/env python3
"""sau-yt: posta vídeo no YouTube pelo Studio, com perfil persistente (padrão do reddit-answers).
  sau-yt login                                  1x: loga na janela, fecha sozinha ao chegar no Studio
  sau-yt upload --file v.mp4 --title T [--desc D] [--visibility private|unlisted|public] [--dry-run] [--show]
Última linha do stdout = URL do vídeo. Sai com erro se a publicação não for confirmada."""
import argparse
import pathlib
import sys

from patchright.sync_api import sync_playwright

PROFILE = pathlib.Path(__file__).parent / ".profile"  # gitignored
RADIO = {"public": "PUBLIC", "unlisted": "UNLISTED", "private": "PRIVATE"}


def upload_done(label):  # "Fazendo upload... 76%" -> ainda subindo; sem % -> subiu (processando/verificando)
    return bool(label) and "%" not in label


def parser():
    p = argparse.ArgumentParser(prog="sau-yt")
    s = p.add_subparsers(dest="action", required=True)
    s.add_parser("login")
    u = s.add_parser("upload")
    u.add_argument("--file", required=True, type=pathlib.Path)
    u.add_argument("--title", required=True)
    u.add_argument("--desc", default="")
    u.add_argument("--visibility", choices=RADIO, default="private")  # padrão privado: público só se pedir
    u.add_argument("--dry-run", action="store_true", help="vai até a tela de visibilidade e não publica")
    u.add_argument("--show", action="store_true", help="janela na tela (padrão: fora da tela)")
    return p


def ctx(p, show):
    return p.chromium.launch_persistent_context(
        str(PROFILE), channel="chrome", headless=False, viewport={"width": 1280, "height": 900},
        args=[] if show else ["--window-position=-3000,-3000"])


def login():
    with sync_playwright() as p:
        c = ctx(p, True)
        pg = c.pages[0] if c.pages else c.new_page()
        pg.goto("https://studio.youtube.com")
        pg.wait_for_url("**/channel/**", timeout=600_000)
        pg.wait_for_timeout(2000)
        c.close()
    print("sessão salva em", PROFILE)


def upload(a):
    if not a.file.is_file():
        sys.exit(f"ERRO: arquivo não existe: {a.file}")
    with sync_playwright() as p:
        c = ctx(p, a.show)
        pg = c.pages[0] if c.pages else c.new_page()
        pg.set_default_timeout(60_000)
        pg.goto("https://www.youtube.com/upload")
        if "accounts.google.com" in pg.url:
            sys.exit("ERRO: sessão expirada, rode: sau-yt login")
        pg.locator('input[type="file"]').first.set_input_files(str(a.file.resolve()))
        pg.locator("#title-textarea #textbox").fill(a.title[:100], timeout=120_000)
        if a.desc:
            pg.locator("#description-textarea #textbox").fill(a.desc)
        pg.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click()
        for _ in range(3):  # detalhes -> elementos -> verificações -> visibilidade
            pg.locator("#next-button").click()
        pg.locator(f"tp-yt-paper-radio-button[name='{RADIO[a.visibility]}']").click()
        # publicar com o upload pela metade corta o envio: espera o rótulo de progresso perder o "%"
        for _ in range(360):  # ponytail: teto de 30 min
            label = pg.locator(".progress-label").first
            if label.count() and upload_done(label.inner_text().strip()):
                break
            pg.wait_for_timeout(5000)
        else:
            sys.exit("ERRO: upload não terminou em 30 min")
        if a.dry_run:
            shot = PROFILE.parent / "dry-run.png"
            pg.screenshot(path=str(shot))
            c.close()
            print(f"dry-run ok (nada publicado), print em {shot}")
            return
        for _ in range(4):  # a lista de sugestões de #hashtag pode engolir o 1º clique: reclica até o diálogo fechar
            pg.locator("#done-button").click(timeout=300_000)  # click espera o botão habilitar
            try:
                pg.locator("ytcp-uploads-dialog").wait_for(state="detached", timeout=20_000)
                break
            except Exception:
                pass
        # publicado = o diálogo de upload fecha e o vídeo (com o título) entra na lista do canal.
        # (o "Link do vídeo" do painel existe antes de publicar, e o diálogo final varia: "processando" x "publicado")
        try:
            pg.goto(pg.url.split("/videos")[0] + "/videos/short")  # Short não aparece na aba "Vídeos"
            row = pg.locator("ytcp-video-row", has_text=a.title[:30]).first
            row.wait_for(timeout=120_000)
            vid = row.locator("a[href*='/video/']").first.get_attribute("href").split("/video/")[1].split("/")[0]
            url = f"https://youtube.com/shorts/{vid}"
        except Exception:
            pg.screenshot(path=str(PROFILE.parent / "erro.png"))
            c.close()
            sys.exit("ERRO: não confirmei a publicação no Studio; print em erro.png (ao lado do yt.py)")
        pg.wait_for_timeout(2000)
        c.close()
        print(url)


if __name__ == "__main__":
    a = parser().parse_args()
    login() if a.action == "login" else upload(a)
