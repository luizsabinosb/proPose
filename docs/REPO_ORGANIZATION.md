# Organizacao do Repositorio

Este documento define convencoes de organizacao para manter o projeto limpo e previsivel, sem impactar o funcionamento da aplicacao.

## Estrutura atual

- `backend/`: API FastAPI e processamento de visao computacional.
- `interface/`: app Flutter (web e macOS).
- `proposing/`: logica de avaliacao de poses reutilizada pelo backend.
- `treinamento/`: scripts de treino e preparo de dados.
- `scripts/`: automacao de execucao, build e limpeza.
- `config/`: configuracoes de empacotamento.
- `ml/pose_info/`, `ml/models/`, `ml/data/`: dados e artefatos de ML.

## Regras de higiene

- Nao versionar logs, caches, builds e PIDs.
- Executar scripts sempre pela raiz do repositorio.
- Evitar criar arquivos temporarios na raiz; preferir pastas dedicadas.
- Qualquer novo script de automacao deve ficar em `scripts/`.

## Convencoes de nome

- Scripts shell: `snake_case.sh`.
- Modulos Python: `snake_case.py`.
- Arquivos de documentacao: `UPPER_SNAKE_CASE.md` para guias internos.

## Sugestao de evolucao (sem mover agora)

Para uma fase futura de refatoracao estrutural, considerar:

- `apps/backend/` e `apps/interface/`
- `ml/treinamento/` (mantendo `ml/models/`, `ml/data/` e `ml/pose_info/`)
- `infra/scripts/` e `infra/config/`

Nesta etapa, a migracao de dados para `ml/` ja foi aplicada sem alterar componentes principais.
