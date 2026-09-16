# Frases e Pensamentos — Criação de Stories

Automação para pesquisar citações verificadas, criar Stories minimalistas e entregar os materiais em um bot do Telegram. A publicação no Instagram não faz parte deste repositório.

## Estado do projeto

MVP em fase de testes. O workflow é executado manualmente e gera **2 Stories por execução**. O agendamento diário será habilitado somente após a homologação editorial e visual.

## Fluxo

1. Pesquisa candidatos com Google Search Grounding.
2. Exige fonte primária ou institucional consultável.
3. Baixa a página indicada e verifica a citação contra o conteúdo da fonte.
4. Rejeita frases sem confirmação suficiente.
5. Evita citações já utilizadas.
6. Renderiza um Story 1080 × 1920 por citação.
7. Envia a arte e a ficha de verificação ao Telegram.
8. Atualiza o histórico no GitHub.

## Política editorial

- Somente citações verificadas.
- Nunca atribuir uma frase com base apenas em sites de frases, Pinterest ou redes sociais.
- Traduções devem ser identificadas como tradução.
- Se a autoria ou o texto não puderem ser confirmados, o candidato é descartado.
- Cada arte contém uma única citação e seu autor.
- A fonte completa é enviada separadamente ao Telegram.

Veja [docs/POLITICA_EDITORIAL.md](docs/POLITICA_EDITORIAL.md).

## Estrutura

```text
.github/workflows/gerar-stories.yml
docs/POLITICA_EDITORIAL.md
src/config.py
src/models.py
src/quote_researcher.py
src/history_manager.py
src/story_renderer.py
src/telegram_bot.py
tests/
main.py
requirements.txt
.env.example
```

## Secrets necessários

Configure em **Settings → Secrets and variables → Actions**:

- `GEMINI_API_KEY`
- `TEST_TELEGRAM_BOT_TOKEN`
- `TEST_TELEGRAM_CHAT_ID`

O bot de testes deve ser criado separadamente no BotFather. A mesma conta pessoal do Telegram pode conversar com esse novo bot; o bot não utiliza o número de telefone como credencial.

## Execução manual

1. Abra **Actions**.
2. Selecione **Gerar Stories de Citações**.
3. Clique em **Run workflow**.
4. Informe opcionalmente a quantidade; o padrão é 2.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Saídas

Durante a execução, as imagens são geradas em `output/`. No GitHub Actions elas são temporárias; a entrega permanente ocorre pelo Telegram. O arquivo `data/history.json` registra os conteúdos utilizados.

## Homologação

Antes de ativar o cron diário, validar:

- autenticidade e rastreabilidade das citações;
- legibilidade em celular;
- textos curtos e longos;
- caracteres acentuados;
- não repetição;
- falhas de fonte e de API;
- recebimento correto no bot de testes.

## Limitações do MVP

A confirmação automatizada depende de a fonte permitir acesso e conter evidência textual suficiente. Quando isso não ocorre, a automação prefere rejeitar uma boa citação a publicar uma atribuição duvidosa.
