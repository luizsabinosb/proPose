# Scripts de Automacao

Todos os scripts devem ser executados a partir da raiz do projeto.

## Execucao

- `./scripts/rodar_macos.sh`: sobe backend e interface macOS.
- `./scripts/rodar_web.sh`: sobe backend (se necessario) e interface web.
- `./scripts/parar_projeto.sh`: encerra backend e Flutter.
- `./scripts/iniciar_backend.sh`: inicia somente o backend.

## Build e limpeza

- `./scripts/build_executable.sh`: gera app empacotado.
- `./scripts/limpar_flutter_macos.sh`: limpa artefatos Flutter/macOS.

## Boas praticas

- Logs e PIDs ficam fora do versionamento.
- Novos scripts devem manter nomes em `snake_case.sh`.
- Preferir scripts idempotentes e com mensagens claras de erro.
