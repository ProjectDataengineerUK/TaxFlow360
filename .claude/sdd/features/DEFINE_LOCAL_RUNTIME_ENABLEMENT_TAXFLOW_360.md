# DEFINE: Habilitação dos Runtimes Locais TaxFlow 360

> Preparar o Windows local com toolchains verificadas para compilar, testar e diagnosticar TaxFlow 360 sem promover ou implantar produção.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

O código local não pode executar os gates JVM, frontend, Terraform e Databricks CLI porque toolchains estão ausentes ou divergentes das versões fixadas. Isso impede detectar erros de compilação antes da CI hospedada e mantém gates obrigatórios bloqueados.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Desenvolvedor local | Implementa e corrige a plataforma | Não consegue compilar Kotlin, Next ou validar Terraform |
| QA/engenharia de plataforma | Reproduz gates de certificação | Ambiente local diverge da matriz de versões |
| Segurança | Controla downloads e supply chain | Precisa de origem, checksum e ausência de privilégios excessivos |
| Maintainer | Atualiza dependências/toolchains | Precisa de diagnóstico e rollback reproduzíveis |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Instalar ou disponibilizar Java/Javac Temurin 21 conforme `.tool-versions` |
| **MUST** | Obter `gradle-wrapper.jar` 8.12.1 da distribuição oficial e validar SHA-256 antes do uso |
| **MUST** | Atualizar/selecionar Node 22.14.0 sem remover silenciosamente a instalação existente |
| **MUST** | Executar `npm ci`, typecheck e build do Control Tower usando o lockfile |
| **MUST** | Instalar Terraform 1.10.5 de origem oficial e executar fmt/validate/test sem cloud apply |
| **MUST** | Instalar Databricks CLI 0.240.0 e validar apenas versão/configuração local, sem autenticar ou deployar |
| **MUST** | Confirmar Python compatível e executar regressão completa com constraints fixadas |
| **MUST** | Executar testes de todos os serviços Gradle/Kotlin |
| **MUST** | Registrar versão, caminho, origem, checksum, comando e resultado de cada toolchain |
| **MUST** | Não armazenar credenciais, alterar cloud, iniciar Docker ou realizar deploy durante esta fase |
| **SHOULD** | Preferir instalação por usuário/gerenciador confiável e PATH explícito, evitando privilégios administrativos quando possível |
| **SHOULD** | Criar preflight automatizado que classifica cada runtime como PASS/BLOCKED/FAIL |

---

## Success Criteria

- [ ] `java` e `javac` reportam Java 21 e executam os testes de todos os serviços Kotlin.
- [ ] `gradlew` valida o wrapper JAR e usa Gradle 8.12.1 com distribuição SHA-256 aprovada.
- [ ] `node --version` reporta 22.14.0 e `npm ci` reproduz o lockfile sem alteração.
- [ ] TypeScript typecheck e Next build terminam sem erro.
- [ ] `terraform version` reporta 1.10.5 e `fmt -check`, `validate` e testes locais terminam sem apply.
- [ ] `databricks version` reporta 0.240.0 sem exigir token ou workspace nesta fase.
- [ ] Python executa 100% dos testes locais existentes sem regressão.
- [ ] Zero executável/toolchain é usado sem origem e integridade registradas.
- [ ] Zero credencial, segredo, recurso cloud ou dado real é criado/usado.
- [ ] O relatório local atualiza apenas os gates realmente executados; externos continuam `BLOCKED`.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| LR-AT-001 | Preflight inicial | Windows atual | Detector executar | Java/Gradle/Terraform/Databricks ausentes e Node divergente são reportados como BLOCKED |
| LR-AT-002 | Java oficial | Distribuição Temurin 21 verificada | PATH da sessão for configurado | `java` e `javac` reportam major 21 |
| LR-AT-003 | Wrapper íntegro | Wrapper JAR oficial baixado | SHA-256 for comparado | Somente checksum esperado libera `gradlew` |
| LR-AT-004 | JVM build | Java/Gradle disponíveis | Todos `*-service` executarem test | Compilação e JUnit produzem evidência por serviço |
| LR-AT-005 | Node selecionado | Node 20 existe e Node 22 foi disponibilizado | Preflight/build executar | Node 22.14.0 é usado sem depender do Node 20 |
| LR-AT-006 | Frontend lock | `package-lock.json` íntegro | `npm ci` executar | Lockfile não muda e dependências são reproduzidas |
| LR-AT-007 | Frontend build | Dependências instaladas | typecheck/build executar | Ambos passam ou falhas ficam registradas para correção |
| LR-AT-008 | Terraform local | Binário 1.10.5 verificado | fmt/validate/test executar | Nenhum apply é chamado e relatórios são preservados |
| LR-AT-009 | Databricks CLI | Binário 0.240.0 verificado | Comando de versão executar | Versão passa sem autenticação/deploy |
| LR-AT-010 | Python regression | Constraints e PYTHONPATH definidos | pytest executar | Suíte permanece verde |
| LR-AT-011 | Integridade inválida | Checksum de download não coincide | Instalador/preflight executar | Artefato é rejeitado e gate fica FAIL |
| LR-AT-012 | Privilégio/rede bloqueados | Instalação exige aprovação ou download falha | Processo executar | Nenhum bypass ocorre; requisito fica BLOCKED com instrução reproduzível |
| LR-AT-013 | Ausência de credenciais | CLIs instaladas sem perfis cloud | Preflight executar | Instalação passa e gates cloud/Databricks hosted continuam BLOCKED |
| LR-AT-014 | Evidência final | Todos os comandos locais executados | Relatório consolidar | Versões, caminhos, checksums, resultados e limitações são listados |

---

## Out of Scope

Explicitly NOT included in this feature:

- Autenticar em AWS, Azure, GCP ou Databricks.
- Executar Terraform plan contra contas reais ou qualquer `apply/destroy`.
- Implantar bundle, pipeline, banco, container ou aplicação.
- Instalar/iniciar Docker Desktop ou alterar sua configuração.
- Usar dados ou regras tributárias reais.
- Gerar release candidate ou marcar gates humanos/hospedados como PASS.
- Remover versões existentes de Node/Python/Java sem aprovação explícita.
- Instalar IDE, extensões ou ferramentas não exigidas pelos gates.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| OS | Windows 10 Pro/PowerShell | Scripts e PATH precisam funcionar em Windows |
| Permission | Downloads/instalações externas podem exigir aprovação | Cada operação de rede/privilégio será solicitada explicitamente |
| Integrity | Toolchains precisam de origem/checksum oficial | Download sem verificação permanece bloqueado |
| Existing state | Node 20, npm, Docker, Git e Python já existem | Preservar instalações e selecionar versões sem remoção destrutiva |
| Security | Nenhuma credencial ou deploy | Apenas comandos locais/offline após downloads |
| Reproducibility | `.tool-versions`, locks e constraints são canônicos | Versão diferente falha no preflight |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.tool-versions`, `gradle/wrapper/`, `package-lock.json`, `constraints-certification.txt`, `tools/preflight/`, `.claude/sdd/reports/` | Toolchains e diagnóstico, não código de domínio |
| **KB Domains** | `testing`, `ci-cd`, `security`, `terraform` | Builds reproduzíveis, checksums e gates locais |
| **IaC Impact** | None | Terraform é validado sem cloud plan/apply |

**Why This Matters:**

- **Location** → evita scripts de instalação misturados aos serviços.
- **KB Domains** → orienta integridade, preflight e evidência.
- **IaC Impact** → instalar Terraform não autoriza alterar infraestrutura.

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| `.tool-versions` | Version manifest | 5 ferramentas | Por revisão | Platform engineering |
| Sites/repos oficiais | HTTPS downloads/checksums | 1 artefato por ferramenta | Por versão fixada | Tool vendors |
| Build/test commands | Process output | Dezenas de gates | Por execução | Engineering |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `tool` | STRING | NOT NULL, unique | No |
| `expected_version` | STRING | NOT NULL | No |
| `actual_version` | STRING | nullable when missing | No |
| `executable_path` | STRING | nullable, redacted user path | Potentially |
| `source_url` | STRING | HTTPS official | No |
| `sha256` | CHAR(64) | required for downloaded binary/archive | No |
| `status` | ENUM | PASS/FAIL/BLOCKED | No |
| `evidence_sha256` | CHAR(64) | required after execution | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Preflight | Antes de cada build local | start → report |
| Toolchain evidence | Mesma execução do build | command → evidence record |

### Completeness Metrics

- 100% das ferramentas fixadas recebem estado explícito.
- 100% dos downloads usados possuem origem e checksum.
- 100% dos gates executados têm saída/evidência; ausentes permanecem BLOCKED.

### Lineage Requirements

- Ferramenta → versão esperada → fonte/checksum → caminho → comando → resultado.
- Build → commit/lockfiles/toolchains → testes → evidência.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| LR-A-001 | Downloads oficiais são permitidos após aprovação | Toolchain correspondente permanece BLOCKED | [ ] |
| LR-A-002 | Instalação por usuário/PATH de sessão é suficiente | Pode ser necessária instalação administrativa | [ ] |
| LR-A-003 | Java 21 e Gradle 8.12.1 compilam todos os projetos atuais | Correções de código/build serão necessárias | [ ] |
| LR-A-004 | Node 22.14.0 é compatível com Next 15.5.0 e lockfile | Dependências/configuração precisarão ser ajustadas | [ ] |
| LR-A-005 | Terraform pode validar módulos sem credenciais em testes locais | Alguns providers permanecerão hosted-only | [ ] |
| LR-A-006 | Databricks CLI permite validação de versão sem autenticação | Gate limita-se à integridade do binário | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Ausências e divergência Node foram medidas |
| Users | 3 | Desenvolvimento, QA, plataforma e segurança cobertos |
| Goals | 3 | Cada runtime e build possui resultado esperado |
| Success | 3 | Versões, comandos, integridade e proibições são mensuráveis |
| Scope | 3 | Instalação local separada de credenciais, cloud e deploy |
| **Total** | **15/15** | Gate de clareza atendido |

---

## Open Questions

- Downloads devem usar `winget`, archives portáveis por usuário ou ambos conforme disponibilidade?
- O usuário autorizará instalação administrativa caso Temurin/Node não funcionem em modo portátil?
- Qual diretório local aprovado armazenará toolchains portáteis sem versioná-las no Git?

O Design deve preferir instalação por usuário e solicitar autorização antes de downloads ou elevação.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | define-agent | Diagnóstico e requisitos iniciais para habilitação local reproduzível |
| 1.1 | 2026-08-17 | design-agent | Design técnico concluído e liberado para Build |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360.md`
