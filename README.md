# sau-tools

**Posta vídeo vertical no YouTube e no TikTok pela linha de comando, controlando o navegador de verdade.** Dois CLIs pequenos, um por rede, pensados pra um agente de código (Claude Code, Codex, Gemini…) ou você mesmo chamar com um comando e ler a última linha da saída.

Nada é publicado sem você pedir: o `sau-yt` sobe como **privado** por padrão e o `--dry-run` para antes de publicar.

```bash
# ensaio: sobe, preenche título e descrição, para na tela de Visibilidade (salva dry-run.png)
sau-yt upload --file /videos/reel.mp4 --title "Meu Short" --dry-run

# de verdade: a última linha do stdout é a URL do vídeo
sau-yt upload --file /videos/reel.mp4 --title "Meu Short" --visibility unlisted
```

## Por que existe

As APIs oficiais de upload exigem app aprovado, cotas e revisão. Aqui a automação usa o próprio Studio / página de upload logados, com a sessão guardada num perfil local. Por isso:

- não há chave de API nem senha no código;
- o upload se comporta como você subindo à mão;
- o custo é manutenção: se a interface da rede mudar, o seletor quebra.

Nasceu como substituto do uploader de YouTube do [social-auto-upload](https://github.com/dreammis/social-auto-upload) (SAU), que dava falso sucesso, quebrava no `set_publish_date` e perdia a sessão por cookie exportado. O TikTok reaproveita o `TiktokVideo` do SAU e só ganha um CLI.

| ferramenta | rede | autenticação | depende de |
|---|---|---|---|
| [`sau-yt/`](sau-yt) | YouTube (Studio) | perfil persistente do Chrome em `sau-yt/.profile/` (`login` uma vez) | [`patchright`](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) + Google Chrome instalado |
| [`sau-tiktok/`](sau-tiktok) | TikTok | cookies em `cookies/` do SAU (`login` uma vez) | clone do [social-auto-upload](https://github.com/dreammis/social-auto-upload) com venv Python 3.12 |

## Requisitos e layout

- macOS (testado) com Google Chrome. Linux deve funcionar; Windows não foi testado.
- Os wrappers (`sau-yt/sau-yt`, `sau-tiktok/sau-tiktok`) chamam o Python de um venv **irmão deste repo**:

```text
ferramentas/
├── _repos/sau-tools/        <- este repo
├── scrapling/.venv/         <- venv que traz o patchright (para o sau-yt)
└── social-auto-upload/.venv/ <- clone do SAU + venv Python 3.12 (para o sau-tiktok)
```

Outro layout? Edite a última linha de cada wrapper (é um `exec` de uma linha) para apontar pro seu Python. Pro `sau-yt` basta qualquer venv com `pip install patchright`.

## sau-yt

```bash
sau-yt login          # 1x: abre o Chrome, você entra na conta; fecha sozinho ao chegar no Studio
sau-yt upload --file /caminho/absoluto/v.mp4 --title "Título" \
              [--desc "..."] [--visibility private|unlisted|public] [--dry-run] [--show]
```

| flag | efeito |
|---|---|
| `--file` | caminho do vídeo (obrigatório; sai com erro se não existir) |
| `--title` / `--desc` | título (obrigatório) e descrição |
| `--visibility` | `private` (padrão), `unlisted` ou `public` |
| `--dry-run` | sobe e para na tela de Visibilidade, deixando rascunho no Studio; salva `dry-run.png` |
| `--show` | mostra a janela (padrão: fora da tela) |

Comportamento:

- A **última linha do stdout é a URL do vídeo**. Se a publicação não for confirmada, sai com código de erro e salva `erro.png`.
- Espera o rótulo de progresso perder o `%` antes de publicar (não depende do idioma do Studio).
- Sessão expirada? Ele avisa `rode: sau-yt login`.
- Sem flag de Short: vertical de até 3 min vira Short sozinho. Não agenda (o Studio tem "Programar"; não implementado).
- Reel republicado como Short: suba privado, espere a checagem de direitos e só então publique. Short com mais de 60 s que recebe claim fica bloqueado.

## sau-tiktok

```bash
sau-tiktok login
sau-tiktok upload-video --file v.mp4 --title "Título" [--tags a,b] [--schedule "AAAA-MM-DD HH:MM"] [--account nome]
```

- Roda com Chrome **visível**: o TikTok recusa headless.
- Teto de 15 min por upload.
- Usa `Cmd+A` pra limpar o título (no Mac, `Control+A` só vai ao início da linha).
- `--account` escolhe qual arquivo de cookie usar (padrão `pedro`; troque pelo seu nome ao fazer o login).

## Testes

Unitários, sem abrir navegador nem tocar na rede:

```bash
cd sau-yt     && ../../../scrapling/.venv/bin/python -m unittest test_yt
cd sau-tiktok && ../../../social-auto-upload/.venv/bin/python -m unittest test_tiktok
```

Validação real: o `sau-yt` foi testado com upload privado. Rode o upload **público** você mesmo; agentes de código costumam bloquear publicação pública pelo shell.

## Segurança

- `sau-yt/.profile/` guarda a sessão logada do seu Google; `cookies/` guarda a do TikTok. Tratam-se como senha. Ambos estão no `.gitignore` (assim como `*.png` de erro). Não os commite nem compartilhe.
- Use só com contas suas e respeitando os termos de cada plataforma. Automação de navegador pode ser limitada ou bloqueada por elas.

## Repos relacionados

Parte do kit de ferramentas do projeto de redes sociais do [@SafeMantella](https://github.com/SafeMantella): [video-cut-pipeline](https://github.com/SafeMantella/video-cut-pipeline) (corte), [transcrever-ptbr](https://github.com/SafeMantella/transcrever-ptbr) (legendas), [social-toolbox](https://github.com/SafeMantella/social-toolbox) (pesquisa), [video-tools](https://github.com/SafeMantella/video-tools) (camadas e slides), [token-kit](https://github.com/SafeMantella/token-kit) (menos token).

## Licença

MIT. Veja [LICENSE](LICENSE).
