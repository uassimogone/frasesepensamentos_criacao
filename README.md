# Frases e Pensamentos — Criação de Stories

Automação gratuita para coletar citações, criar Stories minimalistas e entregar os materiais em um bot do Telegram. A publicação no Instagram não faz parte deste repositório.

## Estado do projeto

MVP em fase de testes. O workflow é executado manualmente e gera **2 Stories por execução**. O agendamento diário será habilitado somente após a homologação editorial e visual.

## Fluxo

1. Consulta páginas públicas gratuitas do Wikiquote em português.
2. Seleciona autores de uma lista curada e descarta entradas marcadas como sem fonte.
3. Evita textos fora do tamanho adequado ou já utilizados.
4. Renderiza um Story 1080 × 1920 por citação.
5. Envia a arte e a ficha de rastreabilidade ao Telegram.
6. Atualiza o histórico no GitHub.

Não há Gemini, cobrança por IA ou qualquer outra API paga neste MVP.

## Política editorial

- A página pública do autor no Wikiquote é a fonte de curadoria e o link é entregue no Telegram.
- Itens marcados como “carece de fontes” são rejeitados.
- Nunca usar Pinterest, redes sociais ou sites genéricos de frases como fonte de curadoria.
- A ficha do Telegram permite conferir o conteúdo antes da publicação.
- Cada arte contém uma única citação e seu autor.

Veja [docs/POLITICA_EDITORIAL.md](docs/POLITICA_EDITORIAL.md).

## Secrets necessários

Configure em **Settings → Secrets and variables → Actions**:

- `TEST_TELEGRAM_BOT_TOKEN`
- `TEST_TELEGRAM_CHAT_ID`

## Execução manual

1. Abra **Actions**.
2. Selecione **Gerar Stories de Citações**.
3. Clique em **Run workflow**.
4. Informe opcionalmente a quantidade; o padrão é 2.

## Homologação

Antes de ativar o cron diário, validar:

- qualidade e rastreabilidade das fontes;
- legibilidade em celular;
- textos curtos e longos;
- não repetição;
- indisponibilidade de fonte;
- recebimento correto no bot de testes.

## Limitação consciente

O Wikiquote é uma fonte gratuita de curadoria, não um arquivo primário de obras. Por isso, a ficha enviada ao Telegram preserva o link e a automação descarta citações que a própria página sinaliza como sem fonte.
