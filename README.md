# sau-tools

Duas ferramentas de linha de comando para postar vídeo vertical por automação de navegador (patchright), cada uma com a sessão guardada num perfil local. Nada é publicado sem você pedir: o `sau-yt` sobe como **privado** por padrão.

| ferramenta | rede | como autentica | depende de |
|---|---|---|---|
| `sau-yt/` | YouTube (Studio) | perfil persistente do Chrome em `sau-yt/.profile/` (`login` 1x) | venv do [Scrapling](https://github.com/D4Vinci/Scrapling) (traz o `patchright`) |
| `sau-tiktok/` | TikTok | cookies em `cookies/` do [social-auto-upload](https://github.com/dreammis/social-auto-upload) (`login` 1x) | clone do SAU com venv Python 3.12 |

Os dois assumem esta pasta dentro de uma `ferramentas/` com `scrapling/` e `social-auto-upload/` irmãs (`ferramentas/_repos/sau-tools/`). Os wrappers têm esse caminho; ajuste se mudar o layout.

## sau-yt

Criado no lugar do uploader de YouTube do SAU, que dava falso sucesso, quebrava com `set_publish_date` e perdia a sessão por cookie exportado.

```bash
sau-yt login                       # 1x: janela visível, fecha sozinha ao chegar no Studio
sau-yt upload --file /caminho/absoluto/v.mp4 --title "Título" [--desc "..."] \
              [--visibility private|unlisted|public] [--dry-run] [--show]
```

- **Padrão é `private`.** Público só com `--visibility public`.
- `--dry-run` sobe o arquivo e para na tela de Visibilidade (deixa rascunho no Studio) e salva `dry-run.png`.
- A última linha do stdout é a URL do vídeo; sai com erro se a publicação não for confirmada (print em `erro.png`).
- Espera o rótulo de progresso perder o `%` antes de publicar (sem depender do idioma do Studio).
- Não há flag de Short: vertical de até 3 min vira Short. Não agenda (o Studio tem "Programar", não implementado).
- Validado com upload privado de teste. Rode o público você mesmo: agentes de código tendem a bloquear publicação pública pelo shell.
- Reel republicado como Short: subir privado, esperar a checagem de direitos e só então publicar; Short com mais de 60 s que recebe claim fica bloqueado.

## sau-tiktok

O SAU não tem `sau tiktok`; isto liga o `TiktokVideo` dele a um CLI.

```bash
sau-tiktok login
sau-tiktok upload-video --file v.mp4 --title T [--tags a,b] [--schedule "AAAA-MM-DD HH:MM"]
```

Roda com Chrome visível (o TikTok recusa headless), tem teto de 15 min e usa `Cmd+A` no título (no Mac `Control+A` só vai ao início da linha).

## Testes

```bash
cd sau-yt && ../../../scrapling/.venv/bin/python -m unittest test_yt
cd sau-tiktok && ../../../social-auto-upload/.venv/bin/python -m unittest test_tiktok
```

## Não commitar

`.profile/` (sessão logada), `cookies/`, prints de erro. Já estão no `.gitignore`.
