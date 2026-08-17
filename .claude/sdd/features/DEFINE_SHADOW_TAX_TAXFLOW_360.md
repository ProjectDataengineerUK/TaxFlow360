# DEFINE: Shadow Tax e Conciliação TaxFlow 360

> Processar operações em paralelo nos modelos atual e futuro, conciliar documento/ERP/pagamento/split e encaminhar divergências explicáveis para revisão humana.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SHADOW_TAX_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Equipes fiscais, financeiras e de pagamentos não conseguem validar continuamente se documento fiscal, ERP, pagamento, split e cálculo tributário permanecem coerentes durante a transição, nem priorizar divergências com explicação, fonte oficial e trilha de revisão.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Equipe fiscal | Revisa tributação e documentos | Identifica diferenças tarde e sem saber qual regra ou campo as originou |
| Financeiro/Tesouraria | Confirma recebimentos e efeitos no caixa | Não distingue diferença tributária de atraso ou falha de liquidação |
| Operações de pagamento/PSP | Processa pagamento, split, estorno e devolução | Precisa encontrar falhas de correlação e conservação financeira |
| Escritório contábil | Monitora vários CNPJs | Precisa de fila consistente sem cruzar dados entre clientes |
| Consultoria tributária | Opera shadow mode para clientes | Precisa medir impacto e revisar exceções com evidência reproduzível |
| Auditor/compliance | Reconstitui decisões e resoluções | Precisa provar entrada, regra, tolerância, reprocessamento, ator e justificativa |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Executar em modo sombra os cálculos atual e CBS/IBS/split sobre a mesma identidade transacional, sem efeito financeiro ou fiscal real |
| **MUST** | Correlacionar documento fiscal, ERP, pagamento e split com identidade, valor, moeda, data, status e versão |
| **MUST** | Classificar divergências de ausência, valor, regra, alíquota, base, arredondamento, status, duplicidade e timing |
| **MUST** | Aplicar tolerâncias versionadas por tipo, moeda, meio de pagamento e janela temporal |
| **MUST** | Preservar memórias de cálculo e links oficiais da Wave 3 em toda divergência tributária |
| **MUST** | Submeter divergências críticas e decisões ambíguas à revisão humana, sem correção automática de regra ou valor |
| **MUST** | Garantir processamento idempotente, replay controlado, eventos tardios, isolamento tenant/CNPJ e histórico imutável |
| **MUST** | Medir taxa de conciliação, materialidade, aging, causa, SLA e reincidência |
| **SHOULD** | Permitir atribuição, comentário, evidência e transição de estado da divergência com RBAC |
| **SHOULD** | Oferecer visão consolidada autorizada por CNPJ, fonte, severidade, regra e período |
| **COULD** | Sugerir causa e próxima ação sem executar correção ou publicar regra |

---

## Success Criteria

- [ ] Correlacionar corretamente pelo menos 99,9% das transações sintéticas elegíveis quando as quatro pontas estiverem presentes.
- [ ] Detectar e publicar 100% das divergências inseridas no conjunto dourado, sem falso `MATCH` crítico.
- [ ] Classificar 100% das divergências com tipo, severidade, materialidade, evidência e próxima ação.
- [ ] Encaminhar 100% das divergências `CRITICAL` para revisão humana e impedir fechamento automático.
- [ ] Processar eventos elegíveis com p95 de detecção de até 5 minutos após chegada da última ponta ou expiração da janela.
- [ ] Reprocessar 100% dos eventos duplicados sem duplicar divergência, reconciliação ou efeito financeiro.
- [ ] Incorporar eventos tardios dentro da janela configurada e criar nova versão auditável quando alterarem o resultado.
- [ ] Rastrear 100% das divergências tributárias até simulação, regra, memória e link oficial.
- [ ] Bloquear 100% das consultas, agregações e revisões cross-tenant automatizadas.
- [ ] Processar o perfil sintético de 100 mil transações sem perda silenciosa dentro do SLO da wave.
- [ ] Não apresentar vulnerabilidade crítica nem divergência crítica de auditoria no gate.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| ST-AT-001 | Match completo | Quatro pontas com mesma identidade e valores dentro da tolerância | A conciliação executar | Uma reconciliação `MATCHED` é publicada sem divergência |
| ST-AT-002 | Ponta ausente | Documento e ERP sem pagamento/split até o fim da janela | O watermark expirar | Divergências `MISSING_SOURCE` são criadas com aging e evidência |
| ST-AT-003 | Valor divergente | Quatro pontas correlacionáveis e uma diferença acima da tolerância | O match executar | `AMOUNT_MISMATCH` registra esperado, realizado, diferença e materialidade |
| ST-AT-004 | Regra divergente | Cálculos atual/futuro usam regras ou alíquotas incompatíveis | O Shadow Tax comparar | Divergência tributária aponta rule IDs, memórias e fontes oficiais |
| ST-AT-005 | Diferença de arredondamento | Valores diferem apenas dentro da tolerância aprovada | A conciliação executar | Resultado é `MATCHED_WITH_TOLERANCE` e registra a tolerância utilizada |
| ST-AT-006 | Evento duplicado | Mesmo evento e chave idempotente chegam várias vezes | O stream reprocessar | Estado e contagens são aplicados uma vez; duplicatas ficam auditadas |
| ST-AT-007 | Evento tardio | Pagamento chega depois da divergência provisória, dentro da janela aceita | O stream incorporar o evento | Nova versão resolve/reclassifica o caso sem apagar o histórico |
| ST-AT-008 | Evento muito tardio | Uma ponta chega depois da retenção configurada | O evento for recebido | Evento segue para tratamento controlado e não altera silenciosamente o fechamento |
| ST-AT-009 | Divergência crítica | Materialidade acima do limite ou risco de segurança/auditoria | O caso for criado | Fica `PENDING_HUMAN_REVIEW` e não pode ser fechado automaticamente |
| ST-AT-010 | Revisão humana | Revisor autorizado recebe um caso | Ele decidir com justificativa/evidência | Ator, decisão, estado anterior/novo e timestamp ficam imutáveis |
| ST-AT-011 | Usuário sem papel | Usuário autenticado sem permissão de revisão | Ele tentar decidir um caso | A ação é negada e auditada |
| ST-AT-012 | Isolamento | Usuário conhece ID de caso de outro tenant | Ele consultar ou revisar | Acesso é negado sem revelar existência ou dados |
| ST-AT-013 | Replay | Checkpoint é restaurado e intervalo reaplicado | O pipeline executar novamente | Checksum, reconciliações e divergências permanecem semanticamente idênticos |
| ST-AT-014 | Escala/freshness | 100 mil transações sintéticas com quatro pontas | O fluxo executar | Eventos são contabilizados sem perda e divergências aparecem no SLO definido |
| ST-AT-015 | Estorno/devolução | Pagamento e split ajustados por evento posterior | O match reavaliar | Valores acumulados respeitam o original e a divergência reflete o estado vigente |

---

## Out of Scope

Explicitly NOT included in this feature:

- Executar recolhimento, liquidação, estorno ou devolução em sistemas reais.
- Corrigir automaticamente documento, ERP, pagamento, split, regra ou alíquota.
- Substituir processo de auditoria, parecer tributário ou aprovação humana.
- Ingerir integrações proprietárias reais sem sandbox, contrato e credenciais aprovadas.
- Implementar Regulatory AI, RAG/base vetorial ou publicação de regras, pertencentes à Wave 6.
- Realizar detecção ML de fraude ou risco de crédito.
- Usar dados pessoais, fiscais ou bancários reais antes dos controles correspondentes.
- Prometer exactly-once do transporte externo; a plataforma garante efeito idempotente no domínio.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Identity | Todas as pontas precisam de identidade/correlação canônica | Registros ambíguos ficam pendentes, nunca são associados por aproximação silenciosa |
| Streaming | Eventos podem chegar fora de ordem, duplicados ou atrasados | Watermark, checkpoint, inbox e versão de estado são obrigatórios |
| Determinism | Mesmo log, regras e tolerâncias devem produzir o mesmo estado | Cutoff e tempo lógico substituem relógio implícito |
| Monetary | Comparações usam Decimal e moeda explícita | `float` não participa de materialidade ou tolerância |
| Governance | Casos críticos exigem revisão humana | Automação não pode fechar ou alterar regra produtiva |
| Security | Tenant/CNPJ delimitam stream, estado, fila e consulta | Particionamento e autorização precedem agregação/revisão |
| Provenance | Divergência tributária herda fontes oficiais da Wave 3 | Shadow Tax não cria catálogo legal paralelo |
| Delivery | Gates externos das waves anteriores continuam registrados | Definição/Design avançam; Ship depende dos gates herdados aplicáveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `contracts/`, `config/`, `services/reconciliation-service/`, `data/databricks/`, `services/query-service/`, `apps/control-tower/`, `tests/` | Reusar reconciliação transacional, lakehouse streaming e consulta tenant-scoped |
| **KB Domains** | `streaming`, `spark`, `data-modeling`, `data-quality`, `lakehouse`, `testing` | Watermark, estado, CDC, idempotência, Delta, contratos e testes |
| **IaC Impact** | Modify existing / streaming test workspace required | Checkpoints, tabelas CDF, jobs e alertas no bundle existente |

**Why This Matters:**

- **Location** → separa decisão/revisão transacional da comparação analítica em streaming
- **KB Domains** → orienta late data, estado, deduplicação, Delta CDF e qualidade
- **IaC Impact** → exige workspace de streaming para provar freshness, replay e checkpoint

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Documento fiscal canônico | Evento/Delta CDF | 100 mil no gate | Near-real-time sintético | Fiscal platform |
| Lançamento ERP | Evento/Delta CDF | 1+ por operação | Near-real-time sintético | ERP integration |
| Pagamento/liquidação | Evento/Delta CDF | 0..N por operação | Conforme meio sintético | Payment domain |
| Split/estorno/devolução | Evento/Delta CDF | 0..N por pagamento | Conforme evento sintético | Payment domain |
| Simulações tributárias | Delta append-only | Atual/futuro por operação | Mesmo cutoff | Tax simulation |
| Política de tolerância | YAML versionado | Dezenas de limites | Por aprovação | Reconciliation governance |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `reconciliation_id` | UUID/STRING | NOT NULL, versioned identity | No |
| `divergence_id` | UUID/STRING | nullable for matched, immutable when present | No |
| `tenant_id` | UUID/STRING | NOT NULL, isolation key | No |
| `company_tax_id` | STRING | NOT NULL, protected | Yes |
| `tax_transaction_id` | STRING | NOT NULL, correlation key | Potentially |
| `event_version` | BIGINT | NOT NULL, monotonic per source identity | No |
| `logical_cutoff_at` | TIMESTAMP_TZ | NOT NULL | No |
| `status` | ENUM | provisional/matched/divergent/pending_review/resolved/invalidated | No |
| `divergence_type` | ENUM | missing/amount/rule/rate/base/rounding/status/duplicate/timing | No |
| `severity` | ENUM | info/review/high/critical | No |
| `expected_amount` | DECIMAL(20,2) | nullable | No |
| `actual_amount` | DECIMAL(20,2) | nullable | No |
| `absolute_difference` | DECIMAL(20,2) | >=0 | No |
| `tolerance_version` | STRING | NOT NULL | No |
| `source_event_ids` | ARRAY<STRING> | NOT NULL | No |
| `simulation_ids` | ARRAY<STRING> | required for tax divergence | No |
| `official_source_ids` | ARRAY<STRING> | required for tax divergence | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Bronze/Silver event availability | Até 2 minutos no ambiente da wave | source timestamp → Silver commit |
| Shadow divergence | p95 até 5 minutos após última ponta/janela | detection timestamp - eligibility timestamp |
| Query/review queue | Até 1 minuto após Gold commit | primeira leitura autorizada |

### Completeness Metrics

- 100% dos eventos contabilizados como correlacionados, pendentes, duplicados ou rejeitados com motivo.
- 100% das reconciliações registram tolerância, cutoff e source event IDs.
- 100% das divergências críticas entram na fila humana.
- 100% das divergências tributárias possuem simulation/rule/source IDs.
- Zero fechamento automático crítico e zero resultado cross-tenant.

### Lineage Requirements

- Reconciliação → documento/ERP/pagamento/split → source event/version/hash.
- Divergência tributária → simulações atual/futura → regra/memória/fonte oficial.
- Estado → evento que causou transição → checkpoint/commit version/cutoff.
- Revisão → ator/papel → estado anterior/novo → justificativa/evidência.
- Replay → intervalo/checkpoint/configuração → checksum antes/depois.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| ST-A-001 | Todas as fontes sintéticas conseguem emitir uma correlação canônica | Seria necessário matching probabilístico fora da wave | [ ] |
| ST-A-002 | Janela tardia inicial de 24 horas cobre os casos sintéticos | Watermark/retenção precisariam ser segmentados por fonte | [ ] |
| ST-A-003 | Especialistas aprovam tolerâncias e materialidades por cenário | Casos só poderiam ser classificados como review | [ ] |
| ST-A-004 | 100 mil transações representam o gate funcional inicial | SLO/particionamento precisariam de novo perfil | [x] |
| ST-A-005 | Um workspace Databricks streaming está disponível | Build ficaria limitado a transformação local/estática | [ ] |
| ST-A-006 | Fila humana pode operar estados e RBAC sem sistema externo de tickets | Seria necessário integrar workflow corporativo | [ ] |
| ST-A-007 | Fontes oficiais e memórias da Wave 3 permanecem imutáveis | Linhagem tributária ficaria incompleta | [x] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Inconsistência entre pontas, transição e revisão estão claras |
| Users | 3 | Seis personas operacionais e de governança identificadas |
| Goals | 3 | Shadow, four-way match, divergências, replay e workflow priorizados |
| Success | 3 | Match, detecção, freshness, idempotência e isolamento mensuráveis |
| Scope | 2 | Fronteiras claras; tolerâncias finais dependem de aprovação especializada |
| **Total** | **14/15** | Gate mínimo atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais tolerâncias monetárias e temporais serão aprovadas por fonte/meio de pagamento?
- Quais limites de materialidade separam `REVIEW`, `HIGH` e `CRITICAL`?
- A janela de 24 horas deve variar por tipo de evento e calendário bancário?
- Quais papéis podem atribuir, decidir, reabrir e invalidar divergências?
- Qual workspace/volume de streaming medirá p95 de 5 minutos, replay e checkpoint?

As perguntas tornam-se configurações e gates governados no Design/Build, sem alterar a fronteira funcional da wave.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | define-agent | Definição inicial da Wave 5 derivada do roadmap e das waves anteriores |
| 1.1 | 2026-08-17 | design-agent | Design técnico concluído e liberado para Build |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_SHADOW_TAX_TAXFLOW_360.md`
