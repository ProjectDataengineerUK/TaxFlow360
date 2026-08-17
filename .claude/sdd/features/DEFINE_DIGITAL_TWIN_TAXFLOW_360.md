# DEFINE: Digital Twin Financeiro TaxFlow 360

> Projetar fluxo de caixa, perda de float tributário, necessidade de capital de giro e cenários de estresse a partir de operações e simulações tributárias sintéticas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | DIGITAL_TWIN_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Equipes financeiras, fiscais e consultorias não conseguem transformar os efeitos temporais de CBS/IBS e split payment em uma projeção reproduzível de caixa, liquidez e capital de giro, nem distinguir impacto tributário de premissas comerciais e financeiras.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| CFO/Tesouraria | Administra liquidez, funding e covenants | Descobre o gap de caixa somente depois de a arrecadação reduzir o valor disponível |
| Equipe financeira | Planeja recebimentos, pagamentos e capital de giro | Não consegue explicar a variação por premissa, tributo e período |
| Equipe fiscal | Valida efeitos da transição tributária | Não enxerga como a vigência tributária altera o caixa |
| Consultoria tributária/financeira | Recomenda plano de adaptação | Precisa comparar cenários auditáveis entre clientes |
| Escritório contábil | Atende vários CNPJs | Precisa projetar cada empresa sem misturar dados ou premissas |
| Banco/fintech | Avalia necessidade potencial de crédito | Precisa de indicadores explicáveis sem transformar a projeção em decisão automática de crédito |
| Auditor/revisor | Reconstitui projeções | Precisa rastrear entradas, cenários, modelos, versões e overrides |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Projetar diariamente entradas, saídas, tributos, split, saldo e caixa mínimo para horizontes configuráveis de 30, 90, 180 e 365 dias |
| **MUST** | Comparar cenários `current`, `cbs_ibs_transition` e `cbs_ibs_split` usando resultados imutáveis da Wave 3 |
| **MUST** | Calcular perda de float tributário, menor saldo, dias abaixo do caixa mínimo, gap máximo e necessidade adicional de capital de giro |
| **MUST** | Executar cenário base e estresses versionados de receita, prazo de recebimento, inadimplência, custos, tributos e disponibilidade de crédito |
| **MUST** | Explicar cada projeção por premissas, dados de origem, versão do modelo e contribuição de cada driver |
| **MUST** | Preservar isolamento por tenant/CNPJ, cutoff lógico, imutabilidade e reprodutibilidade |
| **MUST** | Exibir os links oficiais herdados das simulações tributárias sempre que um indicador depender de regra CBS/IBS ou split |
| **SHOULD** | Oferecer comparação entre projeções e análise de sensibilidade por driver |
| **SHOULD** | Produzir alertas de liquidez classificados por severidade e data esperada |
| **COULD** | Gerar sugestões não vinculantes de renegociação, preço ou funding, sempre identificadas como cenário |

---

## Success Criteria

- [ ] Produzir 100% das projeções com saldo inicial, movimentos diários, saldo final, gap e premissas reconciliáveis.
- [ ] Reproduzir 100% dos valores ao executar o mesmo dataset, cutoff, modelo e conjunto de premissas.
- [ ] Manter erro absoluto zero nos cálculos determinísticos de soma, saldo e capital de giro, respeitada a escala monetária definida.
- [ ] Manter erro percentual absoluto médio de até 15% no backtest de recebimentos sintéticos quando o forecast estatístico estiver habilitado.
- [ ] Processar 100 mil operações em até 15 minutos no ambiente Databricks da wave.
- [ ] Calcular pelo menos seis estresses independentes e três cenários combinados para cada CNPJ elegível.
- [ ] Rastrear 100% dos impactos tributários até a simulação, regra e link oficial correspondentes.
- [ ] Bloquear 100% das consultas ou agregações cross-tenant automatizadas.
- [ ] Preservar 100% das projeções anteriores quando modelo ou premissa receber nova versão.
- [ ] Não apresentar vulnerabilidade crítica nem divergência crítica de auditoria no gate da wave.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| DT-AT-001 | Projeção base | Histórico sintético elegível, saldo inicial e premissas aprovadas | O twin executar 90 dias | Fluxo diário, menor saldo, gap e capital de giro são publicados com linhagem |
| DT-AT-002 | Perda de float | Mesmas operações nos cenários atual e split | Os fluxos forem comparados | A diferença temporal do caixa tributário é isolada e explicada |
| DT-AT-003 | Queda de receita | Cenário base e choque de receita de 10% | O stress test executar | Entradas, saldo e gap refletem exatamente o choque versionado |
| DT-AT-004 | Atraso de recebimento | Recebíveis com prazo e choque de atraso | O cenário executar | Datas de entrada e necessidade de capital mudam sem alterar o valor nominal indevidamente |
| DT-AT-005 | Inadimplência | Carteira sintética e aumento parametrizado de default | O stress executar | Perdas, caixa e severidade são recalculados e explicados |
| DT-AT-006 | Estresse combinado | Receita menor, custo maior e split imediato | O cenário combinado executar | Cada driver e seu efeito marginal permanecem identificáveis |
| DT-AT-007 | Dados insuficientes | CNPJ sem saldo inicial ou série mínima | O twin for solicitado | Resultado oficial não é publicado e as pendências são objetivas |
| DT-AT-008 | Reprodutibilidade | Mesma entrada, cutoff, modelo e premissas | A projeção for repetida | Fingerprint, valores e explicações são idênticos |
| DT-AT-009 | Nova versão | Projeção existente e nova versão de modelo/premissa | O twin recalcular | Novo resultado é criado e o anterior permanece consultável |
| DT-AT-010 | Fonte tributária | Indicador afetado por CBS/IBS/split | O usuário consultar a explicação | Links oficiais, rule IDs e simulation IDs da Wave 3 são exibidos |
| DT-AT-011 | Isolamento | Usuário tenta consultar projeção de outro tenant | A API receber a solicitação | Acesso é negado e auditado sem disclosure |
| DT-AT-012 | Backtest | Janela histórica sintética fechada | O modelo prever período conhecido | MAPE, viés e cobertura são registrados por horizonte |
| DT-AT-013 | Override humano | Premissa automática e override autorizado | A projeção executar | Ator, justificativa, valor anterior/novo e impacto ficam auditáveis |
| DT-AT-014 | 100 mil operações | Perfil sintético da wave | O pipeline executar | Resultado completo é publicado em até 15 minutos sem perdas ou duplicatas |

---

## Out of Scope

Explicitly NOT included in this feature:

- Movimentar dinheiro, contratar crédito ou executar decisão de tesouraria.
- Produzir recomendação vinculante de crédito, rating regulatório ou underwriting automatizado.
- Substituir ERP financeiro, planejamento orçamentário oficial ou opinião profissional.
- Executar Shadow Tax contínuo e conciliação de quatro pontas, pertencentes à Wave 5.
- Implementar Smart Pricing, Tax Profitability completo ou marketplace de crédito, pertencentes ao ecossistema posterior.
- Usar LLM para gerar valores monetários, alterar premissas oficiais ou aprovar cenários.
- Treinar com dados reais antes dos controles de privacidade, consentimento, retenção e segurança.
- Prometer acurácia estatística para CNPJ sem histórico mínimo elegível.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Input | Twin consome contratos canônicos e simulações publicadas das waves anteriores | Não cria parser ou cálculo tributário paralelo |
| Determinism | Cenário determinístico deve ser reproduzível | Cutoff, modelo, premissas e seeds são explícitos |
| Explainability | Todo indicador precisa de drivers e linhagem | Forecast sem explicação suficiente não pode ser oficial |
| Monetary | Somatórios e saldos usam Decimal | `float` não é aceito em valores financeiros finais |
| Modeling | Forecast estatístico precisa de backtest antes da promoção | Modelo insuficiente recua para baseline determinístico |
| Security | Tenant e CNPJ delimitam entrada, modelo e saída | Filtros ocorrem antes de treinamento/agregação |
| Governance | Overrides exigem ator e justificativa | Premissas aprovadas e ad hoc permanecem distinguíveis |
| Delivery | Gates externos anteriores continuam abertos | Definição/Design podem avançar; Ship depende dos gates herdados aplicáveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `contracts/`, `config/`, `data/databricks/`, `services/query-service/`, `apps/control-tower/`, `tests/` | Workload analítico no lakehouse, consulta tenant-scoped pela API |
| **KB Domains** | `spark`, `data-modeling`, `data-quality`, `lakehouse`, `testing` | Janelas temporais, Delta, contratos, qualidade, backtest e reprodutibilidade |
| **IaC Impact** | Modify existing / MLflow test workspace required | Novos jobs, tabelas Gold e registro de modelos no bundle existente |

**Why This Matters:**

- **Location** → mantém o twin fora do caminho transacional e reutiliza o Databricks escolhido
- **KB Domains** → orienta séries temporais, modelagem, qualidade e testes de previsão
- **IaC Impact** → exige workspace para medir SLO, backtest e promoção de modelo

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Operações financeiras canônicas | Delta Silver | 100 mil no gate | Após fechamento do lote | Platform data |
| Simulações tributárias publicadas | Delta/PostgreSQL | Até 3 cenários por operação | Mesmo cutoff do twin | Tax simulation |
| Saldos, recebíveis e pagamentos sintéticos | Delta | Diário por CNPJ | D+0 no lote sintético | Finance data |
| Premissas de cenário | YAML/API versionada | Dezenas por projeção | No instante da execução | Finance governance |
| Modelos/baselines | MLflow/config | Uma versão promovida por horizonte | Por aprovação | Data science/governance |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `projection_id` | UUID/STRING | NOT NULL, UNIQUE, imutável | No |
| `tenant_id` | UUID/STRING | NOT NULL, isolation key | No |
| `company_tax_id` | STRING | NOT NULL, protegido | Yes |
| `scenario_id` | STRING | NOT NULL | No |
| `cutoff_at` | TIMESTAMP_TZ | NOT NULL | No |
| `projection_date` | DATE | NOT NULL | No |
| `opening_cash` | DECIMAL(20,2) | NOT NULL | No |
| `cash_inflow` | DECIMAL(20,2) | NOT NULL | No |
| `cash_outflow` | DECIMAL(20,2) | NOT NULL | No |
| `tax_split_outflow` | DECIMAL(20,2) | >=0 | No |
| `closing_cash` | DECIMAL(20,2) | NOT NULL | No |
| `working_capital_gap` | DECIMAL(20,2) | >=0 | No |
| `model_version` | STRING | NOT NULL | No |
| `assumption_version` | STRING | NOT NULL | No |
| `simulation_ids` | ARRAY<STRING> | NOT NULL | No |
| `explanations` | ARRAY/JSON | NOT NULL, driver/value/lineage | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Eligible Silver inputs | Fechamento validado do lote | Batch completion marker |
| Digital Twin Gold | Até 15 minutos para 100 mil operações | `published_at - input_closed_at` |
| Query API | Resultado disponível em até 1 minuto após publicação | Primeira leitura autorizada |

### Completeness Metrics

- 100% dos dias do horizonte possuem saldo inicial, movimentos e saldo final.
- 100% dos indicadores possuem modelo, premissas, cutoff e linhagem.
- 100% dos impactos tributários referenciam simulation IDs, rule IDs e fontes oficiais herdadas.
- 100% dos overrides possuem ator, justificativa e valores anterior/novo.
- Zero projeção oficial para entrada inelegível ou modelo não promovido.

### Lineage Requirements

- Projeção → dia → movimento → operação/recebível/pagamento canônico.
- Impacto tributário → simulação → regra → fonte oficial clicável.
- Indicador → fórmula/modelo → versão → premissas → aprovador/override.
- Backtest → janela de treino → janela de validação → métricas → decisão de promoção.
- Comparação → projection IDs imutáveis dos cenários comparados.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| DT-A-001 | Dados sintéticos representam sazonalidade, prazos, inadimplência, custos e split | Backtests não cobririam riscos operacionais reais | [ ] |
| DT-A-002 | Há saldo inicial e datas financeiras suficientes por CNPJ | Apenas indicadores parciais poderiam ser publicados | [ ] |
| DT-A-003 | Baseline determinístico é aceitável quando o forecast não passa o gate | A wave dependeria de um modelo estatístico ainda não validado | [ ] |
| DT-A-004 | MAPE de 15% é adequado ao conjunto sintético inicial | Limite precisaria ser segmentado por horizonte/CNPJ | [ ] |
| DT-A-005 | MLflow e workspace Databricks estarão disponíveis | Build ficaria restrito a baseline e testes locais | [ ] |
| DT-A-006 | Resultados da Wave 3 contêm fontes e IDs estáveis | Linhagem tributária do twin seria incompleta | [x] |
| DT-A-007 | O twin é apoio à decisão, não decisão automática de crédito | Exigências regulatórias e de risco ampliariam o escopo | [x] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Efeito do split sobre caixa e falta de explicação estão claros |
| Users | 3 | Sete personas financeiras, fiscais e de governança |
| Goals | 3 | Projeção, estresse, capital de giro, linhagem e fontes priorizados |
| Success | 3 | Reconciliação, backtest, desempenho e isolamento mensuráveis |
| Scope | 2 | Fronteiras claras; thresholds finais de modelo dependem do ambiente sintético |
| **Total** | **14/15** | Gate mínimo atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Qual caixa mínimo e política de liquidez serão usados por perfil sintético?
- Qual histórico mínimo torna um CNPJ elegível ao forecast estatístico?
- O gate de erro deve variar por horizonte, segmento e volatilidade?
- Quais estresses combinados formarão o conjunto oficial inicial?
- Qual workspace/cluster medirá o SLO de 15 minutos e registrará modelos no MLflow?

As respostas tornam-se configurações e gates governados no Design/Build; não alteram a fronteira funcional da wave.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | define-agent | Definição inicial da Wave 4 derivada do roadmap e dos contratos das waves anteriores |
| 1.1 | 2026-08-17 | design-agent | Design concluído com baseline determinístico, forecast governado, stresses e linhagem tributária |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_DIGITAL_TWIN_TAXFLOW_360.md`
