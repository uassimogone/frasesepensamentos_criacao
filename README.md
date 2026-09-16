# Frases e Pensamentos — Criação de Stories

Automação gratuita para coletar citações documentadas, criar Stories minimalistas e entregar os materiais em um bot do Telegram. A publicação no Instagram não faz parte deste repositório.

## Estado do projeto

MVP em fase de testes. O workflow é executado manualmente e gera **2 Stories por execução**. O agendamento diário será habilitado somente após a homologação editorial e visual.

## Fluxo

1. Consulta páginas públicas gratuitas do Wikiquote em português.
2. Aceita somente itens que tragam referência na página consultada.
3. Descarta textos fora do tamanho adequado, sem referência ou já utilizados.
4. Renderiza um Story 1080 × 1920 por citação.
5. Envia a arte e a ficha de rastreabilidade ao Telegram.
6. Atualiza o histórico no GitHub.

Não há Gemini, cobrança por IA ou qualquer outra API paga neste MVP.

## Política editorial

- Somente citações acompanhadas de referência na página pública de origem.
- Nunca usar Pinterest, redes sociais ou sites genéricos de frases como prova de autoria.
- A ficha do Telegram contém o link para conferência antes da publicação.
- Se uma fonte não trouxer referência, o candidato é descartado.
- Cada arte contém uma única citação e seu autor.

Veja [docs/POLITICA_EDITORIAL.md](docs/POLITICA_EDITORIAL.md).

## Secrets necessários

Configure em **Settings → Secrets and variables → Actions**:

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

- qualidade e rastreabilidade das fontes;
- legibilidade em celular;
- textos curtos e longos;
- não repetição;
- indisponibilidade de fonte;
- recebimento correto no bot de testes.

## Limitação consciente

O sistema não inventa nem traduz citações. Por isso, em uma execução excepcional, poderá entregar menos de dois Stories quando as fontes gratuitas não oferecerem candidatos adequados.
