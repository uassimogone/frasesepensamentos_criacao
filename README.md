# Frases e Pensamentos — Criação de Stories

Automação gratuita para pesquisar citações, fazer curadoria por impacto editorial, criar Stories minimalistas e entregar os materiais em um bot do Telegram. A publicação no Instagram não faz parte deste repositório.

## Estado do projeto

O workflow gera **3 Stories por dia**. A execução começa às **05h40 no horário de Brasília**, com margem para que os materiais estejam disponíveis no Telegram até **06h00**. Também pode ser executado manualmente para testes.

## Fluxo

1. Consulta páginas públicas gratuitas do Wikiquote em português.
2. Prioriza autores pouco utilizados nas últimas execuções.
3. Rejeita conteúdo estrangeiro, sem fonte, genérico, excessivamente longo ou já utilizado.
4. Ranqueia as citações por impacto, profundidade, concisão e aderência ao tema editorial.
5. Renderiza um Story 1080 × 1920 por citação.
6. Envia a arte e a ficha de rastreabilidade ao Telegram.
7. Atualiza o histórico no GitHub.

Não há Gemini, cobrança por IA ou qualquer outra API paga neste MVP.

## Política editorial

Cada dia mantém sua identidade visual, fonte e tema, mas a arte mostra somente o rótulo editorial:

- `COMEÇANDO`
- `LUCIDEZ`
- `FORÇA`
- `ATITUDE`
- `CULTURA`
- `VIDA`
- `GRATIDÃO`

- A página pública do autor no Wikiquote é a fonte de curadoria e o link é entregue no Telegram.
- Somente citações em português são aceitas; frases em outros idiomas são descartadas.
- Itens marcados como “carece de fontes” são rejeitados.
- Frases meramente genéricas não atingem a pontuação mínima de impacto.
- Autores recentes recebem menor prioridade para ampliar a diversidade.
- Nunca usar Pinterest, redes sociais ou sites genéricos de frases como fonte de curadoria.
- A ficha do Telegram permite conferir o conteúdo antes da publicação.
- Cada arte contém uma única citação e seu autor, com tipografia em negrito e maior destaque visual.

Veja [docs/POLITICA_EDITORIAL.md](docs/POLITICA_EDITORIAL.md).

## Secrets necessários

Configure em **Settings → Secrets and variables → Actions**:

- `TEST_TELEGRAM_BOT_TOKEN`
- `TEST_TELEGRAM_CHAT_ID`

## Execução manual

1. Abra **Actions**.
2. Selecione **Gerar Stories de Citações**.
3. Clique em **Run workflow**.
4. Informe opcionalmente a quantidade; o padrão é 3.

## Homologação

Na fase de acompanhamento, validar:

- impacto e profundidade da frase;
- diversidade de autores e tradições;
- qualidade e rastreabilidade das fontes;
- legibilidade em celular;
- não repetição;
- recebimento correto no bot de testes.

## Limitação consciente

O Wikiquote é uma fonte gratuita de curadoria, não um arquivo primário de obras. Por isso, a ficha enviada ao Telegram preserva o link e a automação descarta citações que a própria página sinaliza como sem fonte.
