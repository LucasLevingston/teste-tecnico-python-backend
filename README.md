# API de Foco e Produtividade

API em Python com FastAPI para registrar sessões de foco e devolver um diagnóstico simples de produtividade.

## Visão Geral

- Código-fonte em inglês.
- Mensagens e respostas da API em português.
- Persistência em SQLite.
- Documentação automática via Swagger / OpenAPI.
- Testes executados em container separado.

## Requisitos

- Python 3.11+
- Docker e Docker Compose
- `make` opcional para atalhos locais

## Como Executar

### Localmente

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie a API:

```bash
uvicorn main:app --reload
```

### Com Docker

Build da imagem:

```bash
docker build -t foco-prod-api .
```

Execute o container:

```bash
docker run -p 8000:8000 foco-prod-api
```

### Com Docker Compose

Suba o serviço de desenvolvimento:

```bash
docker compose up --build web
```

## Testes

Rodar a suíte em container, com banco isolado para testes:

```bash
docker compose run --rm web_test pytest --cov=. --cov-report=term-missing -q
```

Atalho local:

```bash
make test
```

### Testes automáticos no commit

O repositório inclui um hook de pre-commit que executa a suíte de testes antes de permitir o commit.

Ative os hooks do repositório com:

```bash
git config core.hooksPath .githooks
```

Depois disso, cada `git commit` roda os testes automaticamente e bloqueia o commit se houver falha.

### CI

Também existe um workflow do GitHub Actions que executa os testes em cada push e pull request.

## Documentação da API

Com a aplicação em execução, acesse:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI: `/openapi.json`

## Endpoints

### `POST /registro-foco`

Registra uma sessão de foco.

Campos aceitos:

- `nivel_foco`: inteiro de 1 a 5
- `tempo_minutos`: inteiro maior que 0
- `comentario`: texto com 3 a 1000 caracteres
- `categoria`: opcional, valores `coding`, `meeting`, `estudo` ou `outros`
- `tags`: opcional, lista de strings

### `GET /diagnostico-produtividade`

Retorna o resumo consolidado dos registros salvos, incluindo:

- média do nível de foco
- tempo total registrado
- quantidade de registros
- mensagem de feedback
- categorias com maior tempo acumulado

## Armazenamento

O banco padrão é um arquivo SQLite local (`data.db`). Em Docker Compose, há volumes separados para desenvolvimento e testes.

## Estrutura de Saída

As respostas da API são sempre em português. Exemplos de feedback incluem mensagens como:

- `Você está em uma maratona produtiva de alto nível!`
- `Ótimo foco! Continue com boas práticas e pequenas pausas.`
- `Nível de foco baixo. Pausas estruturadas, bloquear notificações e revisar objetivos podem ajudar.`

## Observações

- O projeto foi desenvolvido com foco em organização, validação e cobertura de testes.
- Caso queira limpar o ambiente de desenvolvimento, remova os volumes do Docker Compose e recrie os containers.
- O código-fonte está em inglês; apenas as mensagens da API ficam em português.
