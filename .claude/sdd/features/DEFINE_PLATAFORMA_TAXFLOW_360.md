# DEFINE: Plataforma TaxFlow 360

> Plataforma SaaS multi-tenant para diagnosticar prontidão, simular CBS/IBS e split payment, projetar impactos financeiros e executar Shadow Tax com resultados auditáveis e equivalentes em múltiplas clouds.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | PLATAFORMA_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Empresas, escritórios contábeis, consultorias e instituições financeiras precisam avaliar, simular e operar a transição para CBS/IBS e split payment sem perder rastreabilidade tributária, previsibilidade de caixa, isolamento entre clientes ou consistência entre fontes de dados e ambientes cloud.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Equipe fiscal | Classifica operações, interpreta regras e valida apurações | Não consegue medir prontidão nem explicar cada resultado com regra, vigência e memória de cálculo |
| Equipe financeira e CFO | Administra caixa, capital de giro, preço e risco | Não enxerga antecipadamente o impacto de CBS/IBS e split payment sobre liquidez |
| Escritório contábil | Opera obrigações e análises para vários CNPJs | Precisa isolar clientes e padronizar diagnósticos sem perder particularidades tributárias |
| Banco, fintech ou PSP | Processa pagamentos e concilia liquidações | Precisa testar split, exceções, estornos e divergências antes da operação real |
| Consultoria tributária | Diagnostica e conduz migrações de clientes | Não possui uma plataforma única, reproduzível e auditável para apoiar recomendações |
| Auditor e administrador | Supervisiona segurança, regras e evidências | Precisa provar quem alterou dados ou regras, quando e com qual fundamento |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Importar XML, CSV e Excel sintéticos e oferecer contratos estáveis para API, webhook, SFTP, ERP, Open Finance, bancos e PSPs |
| **MUST** | Gerar Tax Readiness Score explicável por dimensão, evidência, risco e recomendação |
| **MUST** | Simular modelo atual, CBS, IBS, transição temporal e split payment com regra versionada e memória de cálculo |
| **MUST** | Projetar fluxo de caixa, capital de giro e cenários de estresse no Digital Twin financeiro |
| **MUST** | Executar Shadow Tax e conciliação fiscal, financeira, bancária e tributária com tratamento de divergências |
| **MUST** | Isolar tenants e CNPJs em identidade, dados, eventos, cache, logs, storage e analytics |
| **MUST** | Produzir os mesmos resultados tributários em AWS, Azure e GCP para entradas e versões de regra idênticas |
| **MUST** | Preservar trilha de auditoria imutável para entrada, regra, cálculo, aprovação, reprocessamento e saída |
| **SHOULD** | Disponibilizar Regulatory AI, Copilot tributário, Supplier/Customer Readiness, Smart Pricing, Tax Profitability e simulador bancário nas fases posteriores |
| **SHOULD** | Disponibilizar dashboards específicos para fiscal, financeiro, banco/PSP, consultoria, auditoria e administração |
| **COULD** | Apoiar operação efetiva de split payment após integrações, certificações e autorizações externas |
| **COULD** | Oferecer marketplace de crédito ou recomendações de financiamento após validação do Digital Twin |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

- [ ] Atingir acurácia mínima de 99,5% nos casos tributários dourados revisados.
- [ ] Conciliar corretamente pelo menos 99,9% das transações elegíveis nos cenários sintéticos.
- [ ] Gerar o diagnóstico e seu relatório em até 15 minutos para o perfil de carga definido em cada fase.
- [ ] Processar, em estágios, conjuntos reprodutíveis de 100 mil, 10 milhões e 100 milhões de transações.
- [ ] Obter 100% de equivalência nos valores, regras aplicadas e memórias de cálculo da suíte de paridade executada em AWS, Azure e GCP.
- [ ] Impedir 100% dos acessos cruzados entre tenants nos testes automatizados de isolamento.
- [ ] Registrar 100% das mudanças de regra, aprovações e reprocessamentos com ator, instante, versão e justificativa.
- [ ] Manter zero vulnerabilidade crítica aberta e zero divergência crítica de auditoria no gate de cada release.
- [ ] Colocar 100% dos registros inválidos em quarentena, com motivo estruturado e sem contaminar os cálculos aceitos.
- [ ] Reprocessar eventos idempotentes sem duplicar débito, crédito, pagamento, split ou lançamento de conciliação.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Diagnóstico completo | Um tenant com XML, CSV e Excel sintéticos válidos e dados cadastrais suficientes | A carga for importada e validada | O sistema gera score geral e por dimensão, evidências, riscos e recomendações em até 15 minutos no perfil da fase |
| AT-002 | Entrada inválida | Um arquivo com schema inválido, chaves ausentes ou tipos incompatíveis | A ingestão for executada | O registro é rejeitado ou colocado em quarentena com motivo, origem e correlação, sem entrar nos cálculos |
| AT-003 | Simulação tributária | Uma operação dourada com regra atual, regra CBS/IBS, vigência e resultado esperado | O simulador processar os cenários temporais | Valores e memória de cálculo correspondem ao ground truth com a acurácia mínima definida |
| AT-004 | Split payment simulado | Uma venda com documento, pagamento, meio de pagamento e tributos calculados | O split for simulado | O sistema apresenta valores destinados ao Fisco e à empresa, registra a regra e preserva a soma financeira |
| AT-005 | Digital Twin | Histórico sintético de vendas, recebimentos, pagamentos, estoque e impostos | O cenário base e os stress tests forem executados | O sistema apresenta fluxo de caixa, gap de capital de giro e premissas reproduzíveis por período |
| AT-006 | Shadow Tax | Um fluxo de operações atuais e regras futuras ativas em modo sombra | Os dois modelos forem processados | Todas as operações recebem correlação e as diferenças tributárias e financeiras são classificadas |
| AT-007 | Conciliação de quatro pontas | Documento fiscal, ERP, pagamento, split e visão fiscal correlacionáveis | A conciliação for executada | Pelo menos 99,9% das transações elegíveis fecham corretamente e as demais geram divergência auditável |
| AT-008 | Isolamento multi-tenant | Dois tenants com usuários, CNPJs e dados distintos | Um usuário consultar APIs, dashboards, logs ou analytics | Somente recursos autorizados do próprio tenant são retornados; tentativas cruzadas são negadas e auditadas |
| AT-009 | Idempotência | O mesmo evento com a mesma chave idempotente entregue mais de uma vez | Consumidores e engines o processarem | O estado financeiro e tributário é aplicado uma única vez e as duplicatas ficam registradas |
| AT-010 | Regra fora de vigência | Uma operação cuja data não pertence à vigência da regra solicitada | O Tax Engine calcular | A regra não é aplicada; o sistema seleciona uma versão válida ou retorna erro explicável |
| AT-011 | Governança regulatória | Uma proposta de mudança gerada por usuário ou Regulatory AI | A proposta for submetida sem aprovação humana | A regra produtiva permanece inalterada até aprovação autorizada e registrada |
| AT-012 | Paridade multi-cloud | O mesmo dataset, configuração e catálogo de regras implantados em AWS, Azure e GCP | A suíte de conformidade for executada | Valores, decisões e memórias de cálculo são equivalentes em 100% dos casos |
| AT-013 | Escala progressiva | Os datasets determinísticos de 100 mil, 10 milhões e 100 milhões estiverem disponíveis | Cada gate de carga for executado | O volume previsto para a fase conclui dentro do SLO definido, sem perda ou duplicação silenciosa |
| AT-014 | Falha transitória | Um serviço dependente ficar temporariamente indisponível | A política de retry for acionada | O processamento retoma com backoff e idempotência; após o limite, o evento segue para tratamento controlado |
| AT-015 | Trilha de auditoria | Um cálculo for criado, recalculado ou afetado por mudança de regra | Um auditor solicitar sua história | A plataforma reconstrói entrada, versão da regra, memória, ator, aprovações e saídas sem lacunas |

---

## Out of Scope

Explicitly NOT included in this feature:

- Substituir juridicamente a validação de especialistas tributários ou emitir opinião legal autônoma.
- Alterar regras produtivas automaticamente a partir de IA ou de fontes regulatórias sem aprovação humana.
- Movimentar ou custodiar recursos financeiros na fase de simulação; a operação efetiva de split depende de integrações, contratos, certificações e autorizações externas.
- Ingerir dados pessoais ou fiscais reais antes da aprovação dos controles de segurança, privacidade, retenção e anonimização.
- Manter Snowflake e Databricks simultaneamente no escopo inicial da plataforma de dados.
- Prometer cobertura de conectores proprietários sem documentação, credenciais, sandbox e contrato de integração do fornecedor.
- Definir nesta fase a decomposição final de microsserviços, tecnologias de cada serviço ou topologia detalhada; essas decisões pertencem ao DESIGN.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Regulatory | Toda regra deve possuir vigência, versão, fundamento, autoria e aprovação | O modelo precisa preservar temporalidade e governança desde a Fundação |
| Accuracy | Acurácia tributária mínima de 99,5% nos casos validados | Releases dependem de suíte dourada e análise explícita das divergências |
| Reconciliation | Conciliação mínima de 99,9% das transações elegíveis | Exige identidade transacional, tolerâncias formais e classificação das exceções |
| Security | Zero vulnerabilidade crítica e isolamento multi-tenant integral | Segurança e tenancy são gates, não funcionalidades posteriores |
| Audit | Toda decisão relevante deve ser reconstruível | Entradas, versões, cálculos e aprovações não podem ser sobrescritos sem histórico |
| Architecture | Núcleo tributário independente de cloud e do Databricks | Serviços de domínio não podem depender de APIs proprietárias para calcular |
| Platform | Databricks, Delta Lake e Unity Catalog no plano de dados/IA | Simulações massivas, analytics e ML devem usar contratos claros com o plano transacional |
| Multi-cloud | AWS, Azure e GCP devem passar pela mesma suíte de paridade | IaC e adaptadores específicos não podem alterar semântica de negócio |
| Data | Desenvolvimento inicial usa dados sintéticos determinísticos | Integrações reais entram somente após contratos e controles aprovados |
| Delivery | O produto completo será entregue em fases SDD | Cada fase deve ter DEFINE, DESIGN, BUILD, testes e SHIP próprios ou decomposição rastreável |
| Performance | Diagnóstico em até 15 minutos no perfil acordado por fase | Cada perfil de carga precisa declarar infraestrutura e SLO antes do teste |
| Operations | Falhas devem ser idempotentes, observáveis e recuperáveis | Retry, quarentena e reprocessamento precisam manter consistência |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/`, `contracts/`, `data/`, `integrations/`, `deploy/`, `validation/` | Separar domínio, contratos, dados, conectores, infraestrutura e evidências de validação |
| **KB Domains** | `streaming`, `data-modeling`, `data-quality`, `lakehouse`, `medallion`, `cloud-platforms`, `lakeflow`, `aws`, `terraform`, `genai`, `testing` | Consultar Kafka, contratos, modelagem temporal, Delta/Databricks, multi-cloud, IaC, guardrails e testes |
| **IaC Impact** | New resources | Criar fundação multi-cloud, módulos Terraform, ambientes, identidade, rede, dados, eventos, observabilidade e Databricks |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `.claude/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Data Contract (if applicable)

> Include this section when the feature involves data pipelines, ETL, or analytics.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Gerador sintético | XML / CSV / Excel / evento canônico | 100 mil, 10 milhões e 100 milhões de transações | Sob demanda e streaming controlado | Engenharia de qualidade |
| ERP, PDV e e-commerce | API / webhook / SFTP / arquivo | A definir por conector | Contrato deve suportar batch e near-real-time | Integrações |
| Bancos, PSPs e Open Finance | API / eventos / arquivos de conciliação | A definir por instituição | Contrato deve declarar SLA por fonte | Integrações financeiras |
| Catálogo regulatório | Legislação, regras validadas e metadados | Baixo volume, alta criticidade | Por vigência e publicação aprovada | Governança tributária |
| Sistema fiscal de referência | API / exportação controlada | Conforme suíte dourada | Por ciclo de validação | Validação tributária |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `tax_transaction_id` | VARCHAR | NOT NULL, UNIQUE, imutável | No |
| `tenant_id` | UUID/VARCHAR | NOT NULL, chave de isolamento | No |
| `company_tax_id` | VARCHAR | NOT NULL, validado e protegido | Yes |
| `source_system` | VARCHAR | NOT NULL, enum versionado | No |
| `source_event_id` | VARCHAR | NOT NULL com `source_system`, chave idempotente | No |
| `occurred_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | No |
| `document_type` | VARCHAR | Enum versionado | No |
| `document_key` | VARCHAR | Protegido, unicidade definida por fonte | Yes |
| `operation_amount` | DECIMAL | NOT NULL, escala monetária explícita | No |
| `currency` | CHAR(3) | NOT NULL, padrão ISO 4217 | No |
| `rule_version` | VARCHAR | NOT NULL para resultado calculado | No |
| `calculation_status` | VARCHAR | NOT NULL, enum versionado | No |
| `payload_schema_version` | VARCHAR | NOT NULL | No |
| `ingested_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Ingestão batch | Carga aceita ou quarentenada dentro do orçamento do perfil | Tempo entre início e resultado da validação |
| Eventos Shadow Tax | SLA específico definido no DESIGN da fase antes da produção | Diferença entre `occurred_at` e processamento confirmado |
| Bronze | Dentro do SLA da fonte após aceitação | Comparação de timestamp e contagem de origem |
| Silver | Dentro do SLA da fase após Bronze | Conclusão de validação, deduplicação e normalização |
| Gold | Diagnóstico completo em até 15 minutos no perfil acordado | Tempo entre fechamento da entrada e publicação do relatório |

### Completeness Metrics

- 100% dos registros recebidos devem terminar como aceitos, rejeitados ou em quarentena; nenhum pode desaparecer silenciosamente.
- 100% dos registros aceitos devem possuir `tenant_id`, identidade de origem, versão de schema e instante de ingestão.
- Zero chave nula em `tax_transaction_id` e zero duplicação de efeito para a mesma chave idempotente.
- Pelo menos 99,9% das transações elegíveis devem ser conciliadas corretamente.
- Totais monetários de entrada, segregação e saída devem respeitar as invariantes definidas por cenário.

### Lineage Requirements

- Linhagem do campo de origem até score, cálculo, projeção, divergência e dashboard.
- Relação explícita entre documento, pedido, pagamento, parcela, split, regra, crédito, estorno e devolução.
- Análise de impacto obrigatória antes de publicar alterações de schema ou regra.
- Preservação das versões de dados e regras usadas em cada cálculo e reprocessamento.
- Identificação de tenant e classificação de sensibilidade propagadas por todas as camadas.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Databricks oferece os recursos necessários nas regiões e clouds escolhidas para cada cliente | Pode exigir região alternativa, residência de dados diferente ou outro plano analítico | [ ] |
| A-002 | Serviços gerenciados de Kafka ou compatíveis preservam os contratos e garantias exigidos nas três clouds | Pode exigir Kafka autogerenciado ou Confluent como camada comum | [ ] |
| A-003 | Casos dourados podem ser produzidos e aprovados por especialistas em quantidade suficiente | Sem ground truth, a meta de acurácia não pode ser demonstrada | [ ] |
| A-004 | Sistemas fiscais de referência permitem exportação ou integração para comparação | Pode limitar a terceira fonte de validação e exigir processo manual | [ ] |
| A-005 | Dados sintéticos conseguem representar regimes, exceções, créditos, cancelamentos, estornos e falhas reais | Lacunas só apareceriam tardiamente com dados reais | [ ] |
| A-006 | O mesmo modelo canônico atende empresas, contadores, consultorias e bancos/PSPs | Pode exigir contratos de domínio separados e tradução adicional | [ ] |
| A-007 | O orçamento suporta infraestrutura e testes de paridade nas três clouds | Pode exigir ativação progressiva por provedor sem alterar a arquitetura-alvo | [ ] |
| A-008 | A legislação e os leiautes necessários estarão disponíveis e versionáveis durante o desenvolvimento | Mudanças ou ausência de especificação podem bloquear cenários regulatórios | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Usuários, transição tributária e impactos estão descritos de forma específica e acionável |
| Users | 3 | Seis personas possuem papéis e dores explícitas |
| Goals | 3 | Capacidades estão priorizadas por MoSCoW e vinculadas aos quatro módulos e à fundação |
| Success | 3 | Metas quantitativas cobrem acurácia, conciliação, tempo, escala, paridade, segurança e auditoria |
| Scope | 3 | Incluídos, adiados e excluídos estão separados; decisões técnicas detalhadas foram reservadas ao DESIGN |
| **Total** | **15/15** | Gate mínimo de 12/15 atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Validar antes do DESIGN as regiões-alvo e a disponibilidade do Databricks em cada cloud.
- Definir o orçamento e o calendário de ativação dos ambientes AWS, Azure e GCP.
- Nomear responsáveis pela aprovação dos casos dourados e das regras tributárias.
- Definir, por perfil de carga, o SLO detalhado de ingestão e Shadow Tax.
- Confirmar quais sistemas fiscais e ERPs fornecerão sandboxes ou exportações nas fases de integração.

Essas questões são riscos de planejamento e escolhas de arquitetura; não alteram o problema, os usuários, o escopo funcional ou os critérios de sucesso definidos.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-14 | define-agent | Initial version derived from approved brainstorm |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_PLATAFORMA_TAXFLOW_360.md`
