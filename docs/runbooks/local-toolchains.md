# Toolchains locais

Este fluxo instala versões portáteis e verificadas sem alterar o PATH permanente nem configurar credenciais de nuvem.

1. Revise `config/local-toolchains.yaml` e as origens oficiais.
2. Execute, após aprovação de rede, `tools/preflight/bootstrap-toolchains.ps1 -Tool <nome>` para cada ferramenta.
3. Na sessão que executará os testes, use `. tools/preflight/activate-toolchains.ps1`.
4. Rode `python -m taxflow_preflight.cli detect --repository .` com `PYTHONPATH=tools/preflight/src`.

O bootstrap verifica HTTPS, host permitido, tamanho, SHA-256 e travessia de caminho antes da extração. O Gradle Wrapper é o único artefato escrito no repositório. Terraform local aceita somente `version`, `fmt`, `validate` e `test`; implantação e credenciais permanecem fora do escopo.

Para reverter, feche a sessão PowerShell. A remoção do cache deve ser feita somente após conferir que o caminho resolve para `%LOCALAPPDATA%\TaxFlow360\tool-cache` ou para o valor explícito de `TAXFLOW_TOOL_CACHE`.

Origens: [Eclipse Temurin](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.5%2B11), [Node.js](https://nodejs.org/download/release/v22.14.0/SHASUMS256.txt), [Gradle](https://gradle.org/release-checksums/), [Terraform](https://releases.hashicorp.com/terraform/1.10.5/terraform_1.10.5_SHA256SUMS) e [Databricks CLI](https://github.com/databricks/cli/releases/tag/v0.240.0).
