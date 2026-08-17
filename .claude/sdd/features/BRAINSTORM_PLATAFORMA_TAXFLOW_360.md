# BRAINSTORM: Plataforma TaxFlow 360

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | PLATAFORMA_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** Construir a plataforma completa TaxFlow 360 com Diagnóstico de Prontidão, Simulador Tributário, Digital Twin Financeiro e Shadow Tax, preparada para todas as fontes de dados, inicialmente validada com dados sintéticos e entregue em fases pelo fluxo SDD.

**Context Gathered:**
- O projeto ainda não possui código de aplicação; `context.md` concentra a visão de produto, arquitetura e estratégia.
- O produto atenderá empresas, escritórios contábeis, bancos/PSPs e consultorias, com operação multiempresa e controle de acesso por perfil.
- O núcleo tributário deve ser transacional, determinístico, auditável e independente da cloud; Databricks será a plataforma de dados, analytics e IA.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/`, `data/`, `contracts/`, `integrations/`, `deploy/` | Separar domínio, ingestão, contratos, conectores, dados e infraestrutura |
| Relevant KB Domains | `streaming`, `data-modeling`, `data-quality`, `lakehouse`, `medallion`, `cloud-platforms`, `lakeflow`, `aws`, `terraform`, `genai`, `testing` | Aplicar padrões de eventos, contratos, Delta/Databricks, multi-cloud, IaC e validação |
| IaC Patterns | Terraform modular, ainda sem implementação | Criar módulos comuns e módulos específicos para AWS, Azure e GCP |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual deve ser o primeiro produto validável? | Os quatro módulos: Diagnóstico, Simulador, Digital Twin e Shadow Tax | A visão cobre o fluxo tributário e financeiro completo |
| 2 | Qual estratégia de escopo? | Plataforma completa com profundidade, desenvolvida em fases | O roadmap mantém todos os módulos, mas evita uma construção monolítica |
| 3 | Quem serão os usuários da primeira versão? | Empresa, escritório contábil, banco/PSP e consultoria | Multi-tenancy, multiempresa e RBAC são requisitos de fundação |
| 4 | Quais fontes de dados devem ser suportadas? | Preparar o código para todas; começar com dados sintéticos | Usar modelo canônico e arquitetura de conectores desde o início |
| 5 | Qual será a fonte de verdade dos cálculos? | Especialista + legislação oficial + sistema fiscal de referência, com revisão humana das divergências | Exige suíte de casos dourados, proveniência e aprovação auditável |
| 6 | Como medir prontidão para uso real? | Acurácia tributária ≥ 99,5%, conciliação ≥ 99,9%, relatório ≤ 15 minutos e zero divergência crítica | Define SLOs e gates quantitativos de qualidade |
| 7 | Qual modelo de implantação? | SaaS multi-tenant em AWS, Azure e GCP | Requer núcleo portátil, adaptadores cloud e testes de paridade |
| 8 | Qual escala dos dados sintéticos? | Progressiva | Criar níveis de 100 mil, 10 milhões e 100 milhões de transações |

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | A criar em `data/synthetic/` | 3 perfis de carga | XML fiscal, CSV, Excel e eventos canônicos; 100 mil, 10 milhões e 100 milhões de transações |
| Output examples | A criar em `validation/expected/` | 1 conjunto por cenário/regra | Score, memória de cálculo, split simulado, fluxo de caixa e divergências |
| Ground truth | A criar em `validation/golden/` | Cobertura por regra e caso limítrofe | Combinação de especialista, legislação oficial e sistema fiscal de referência |
| Related code | N/A | 0 | Não há código de aplicação existente |

**How samples will be used:**

- Validar contratos, conectores e qualidade dos dados de entrada.
- Executar testes determinísticos do motor tributário e da memória de cálculo.
- Medir acurácia, conciliação, tempo de processamento e paridade entre clouds.
- Produzir fixtures reprodutíveis para readiness, simulação, Digital Twin e Shadow Tax.

---

## Approaches Explored

### Approach A: Núcleo portátil + adaptadores cloud + Databricks multi-cloud ⭐ Recommended

**Description:** Um núcleo tributário e financeiro único, containerizado e independente de cloud, conectado a serviços gerenciados por adaptadores. Databricks, Delta Lake e Unity Catalog formam o plano de dados e IA nas três nuvens.

**Pros:**
- Mantém regras, resultados e memória de cálculo consistentes entre clouds.
- Permite usar serviços gerenciados sem acoplar o domínio tributário ao provedor.
- Databricks atende simulações massivas, streaming, ML, Digital Twin e Shadow Tax.
- Contratos de dados e Kafka desacoplam o plano transacional do analítico.

**Cons:**
- Exige interfaces cloud rigorosas e uma suíte de conformidade multi-cloud.
- A operação e o custo de três provedores elevam a complexidade desde o início.

**Why Recommended:** O `context.md` exige núcleo cloud-independent e recomenda Databricks para dados/IA. Os KBs de Kafka, contratos de dados e Terraform sustentam o desacoplamento e a modularização. Confiança 0,85: há forte precedente no KB, mas ainda não há código do projeto para validar a adaptação.

---

### Approach B: Plataforma totalmente autogerenciada

**Description:** Operar Kubernetes, Kafka, PostgreSQL, storage e observabilidade de maneira uniforme nas três nuvens.

**Pros:**
- Máxima uniformidade de infraestrutura.
- Menor dependência de serviços proprietários.

**Cons:**
- Alto custo operacional e maior superfície de segurança.
- A equipe assume upgrades, backups, disponibilidade e recuperação de todos os componentes.

---

### Approach C: Implementação nativa por nuvem

**Description:** Criar uma arquitetura distinta e otimizada para AWS, Azure e GCP.

**Pros:**
- Integração máxima com cada ecossistema.
- Possibilidade de otimização individual de custo e desempenho.

**Cons:**
- Triplica caminhos de implementação e manutenção.
- Aumenta o risco de divergência funcional e tributária entre clouds.

---

## Data Engineering Context (if applicable)

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Dados sintéticos fiscais e financeiros | XML / CSV / Excel / eventos | 100 mil → 10 milhões → 100 milhões de transações | Batch e streaming simulados |
| ERP, PDV e e-commerce | API / webhook / SFTP | Desconhecido | Contratos preparados; integração posterior |
| Bancos, PSPs e Open Finance | API / eventos | Desconhecido | Contratos preparados; integração posterior |

### Data Flow Sketch

```text
[Fontes] → [Ingestion Gateway] → [Contrato + Qualidade + Tenant]
                                      ↓
                                    [Kafka]
                         ┌────────────┴────────────┐
                         ↓                         ↓
               [Plano transacional]       [Lakehouse Databricks]
              PostgreSQL/Redis/Engines    Bronze → Silver → Gold
                         ↓                         ↓
                  [Auditoria]          [Score/Twin/Shadow/IA]
                         └────────────┬────────────┘
                                      ↓
                              [APIs e Dashboards]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o volume esperado? | Perfis progressivos até 100 milhões de transações | Exige particionamento, processamento distribuído e testes de carga |
| 2 | Qual freshness é necessária? | Batch para cargas históricas e streaming para Shadow Tax | Exige dois modos de ingestão sob o mesmo contrato canônico |
| 3 | Quem consome o resultado? | Fiscal, financeiro, contadores, consultorias, bancos/PSPs e executivos | Exige RBAC, visões por persona e isolamento multi-tenant |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Núcleo portátil + adaptadores cloud + Databricks multi-cloud |
| **User Confirmation** | 2026-08-14 |
| **Reasoning** | Preserva o Databricks recomendado no contexto, mantém o cálculo transacional fora da plataforma analítica e permite paridade entre AWS, Azure e GCP |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Implementar a plataforma inteira por fases SDD | Manter profundidade sem construir tudo de forma monolítica | MVP descartável ou entrega única sem gates |
| 2 | Usar Databricks no plano de dados e IA | Adequado para simulação massiva, streaming, ML e governança | Snowflake junto com Databricks no início |
| 3 | Manter o Tax Engine fora do Databricks | Garantir baixa latência, determinismo e auditabilidade transacional | Cálculo crítico concentrado no lakehouse |
| 4 | Suportar AWS, Azure e GCP com adaptadores | Preservar um único domínio e permitir serviços gerenciados | Três bases funcionais independentes |
| 5 | Validar inicialmente com dados sintéticos progressivos | Permitir desenvolvimento seguro e testes reproduzíveis antes de dados reais | Dependência imediata de integrações externas |
| 6 | Usar três fontes de verdade | Reduzir risco de erro regulatório e operacional | Uma única referência sem revisão humana |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Nenhuma removida permanentemente | O usuário confirmou a visão completa | N/A |
| Regulatory AI, Copilot e módulos complementares na Fundação | Não são necessários para validar contratos, isolamento e núcleo transacional; foram movidos para a Fase 6 | Sim, já planejados |
| Integrações reais na Fundação | Dados sintéticos permitem validar o modelo canônico antes de depender de terceiros; conectores reais entram por fases | Sim, já planejadas |
| Operação real de split payment nas fases iniciais | O mecanismo começa como simulação até existirem integração, certificação e autorização operacional | Sim, após validação e integração |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Faseamento do produto | ✅ | Aprovado; manter todas as funcionalidades e desenvolver por SDD | Sim — recursos foram adiados, não eliminados |
| Arquitetura, fluxo de dados e falhas | ✅ | Aprovado | Não |
| Abordagem multi-cloud | ✅ | Databricks precisava permanecer como recomendação do `context.md` | Sim — Approach A revisada para Databricks multi-cloud |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

Empresas e instituições financeiras precisam avaliar, simular e operar a transição para CBS/IBS e split payment sem perder rastreabilidade tributária, previsibilidade de caixa ou consistência entre sistemas, fontes de dados e ambientes cloud.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Equipes fiscais e financeiras | Baixa visibilidade sobre prontidão, tributação futura e impacto no caixa |
| Escritórios contábeis | Necessidade de operar múltiplos CNPJs com regras, dados e riscos diferentes |
| Bancos, fintechs e PSPs | Necessidade de simular split, reconciliar pagamentos e demonstrar prontidão operacional |
| Consultorias tributárias | Falta de plataforma auditável para diagnóstico, migração e acompanhamento de clientes |

### Success Criteria (Draft)

- [ ] Atingir acurácia tributária mínima de 99,5% nos casos validados.
- [ ] Conciliar corretamente pelo menos 99,9% das transações.
- [ ] Gerar diagnóstico e relatório em até 15 minutos após a importação no perfil de carga acordado para a fase.
- [ ] Não apresentar divergência crítica de segurança ou auditoria.
- [ ] Produzir resultados equivalentes em AWS, Azure e GCP para a suíte de conformidade.
- [ ] Processar os perfis sintéticos de 100 mil, 10 milhões e 100 milhões de transações nas etapas previstas.

### Constraints Identified

- SaaS multi-tenant com isolamento integral de dados, eventos, cache, logs e analytics.
- Núcleo tributário independente de cloud e separado do plano analítico.
- Databricks como plataforma de dados, analytics, simulações massivas, ML e IA.
- Regras versionadas por vigência, com fundamento legal, memória de cálculo e aprovação humana.
- Fontes reais desacopladas por contratos e conectores; início com dados sintéticos.
- Paridade funcional e de cálculo entre AWS, Azure e GCP.

### Out of Scope (Confirmed)

- Nenhuma funcionalidade da visão geral foi excluída permanentemente.
- Integrações reais e operação efetiva de split ficam fora da Fundação e entram nas fases correspondentes.
- Regulatory AI, Copilot e módulos complementares não bloqueiam as fases centrais e entram na Fase 6.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 8 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 0 permanentes; 3 grupos adiados por fase |
| Validations Completed | 3 |
| Duration | Uma sessão colaborativa |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_PLATAFORMA_TAXFLOW_360.md`
