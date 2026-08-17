# DEFINE: Diagnóstico de Prontidão TaxFlow 360

> Avaliar dados fiscais, financeiros e operacionais de cada empresa e produzir um Tax Readiness Score explicável, versionado e acionável.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | READINESS_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Equipes fiscais, financeiras, escritórios contábeis e consultorias não conseguem medir objetivamente se cada CNPJ possui dados, processos, integrações e controles suficientes para operar CBS/IBS e split payment, nem explicar quais evidências sustentam o diagnóstico.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Equipe fiscal | Responsável por cadastros, documentos e regras | Não identifica lacunas que impedem cálculos e conformidade futuros |
| Equipe financeira/CFO | Responsável por caixa e pagamentos | Não enxerga riscos de conciliação, liquidez e split readiness |
| Escritório contábil | Opera múltiplos CNPJs | Precisa comparar clientes mantendo isolamento e critérios consistentes |
| Consultoria tributária | Conduz diagnóstico e migração | Precisa justificar recomendações com evidências reproduzíveis |
| Auditor/administrador | Revisa metodologia e acesso | Precisa reconstruir versão, pesos, evidências e ator do assessment |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Consumir somente transações canônicas aceitas pela Fundação, isoladas por tenant e CNPJ |
| **MUST** | Calcular score geral de 0 a 100 e scores por dimensão: fiscal, financeiro, ERP/integrações, cadastro, meios de pagamento, conciliação, split readiness e capital de giro |
| **MUST** | Associar cada score a evidências, regra de pontuação, severidade, risco e recomendação acionável |
| **MUST** | Versionar metodologia, pesos, limiares e instante do assessment, preservando resultados históricos |
| **MUST** | Gerar diagnóstico em até 15 minutos para 100 mil transações sintéticas depois do fechamento da entrada |
| **MUST** | Impedir leitura ou agregação entre tenants e registrar auditoria de execução e consulta |
| **SHOULD** | Permitir comparação temporal do mesmo CNPJ e visão consolidada autorizada de múltiplos CNPJs |
| **SHOULD** | Exportar relatório estruturado e apresentação executiva em formatos adequados à API e ao dashboard |
| **COULD** | Permitir simulação de alteração de pesos sem substituir a metodologia oficial publicada |

---

## Success Criteria

- [ ] Processar 100.000 transações sintéticas e publicar o assessment completo em até 15 minutos no ambiente de teste da wave.
- [ ] Produzir exatamente um score geral e oito scores dimensionais entre 0 e 100 para cada CNPJ elegível.
- [ ] Garantir que 100% dos pontos concedidos ou descontados possuam pelo menos uma evidência rastreável ou uma justificativa explícita de ausência.
- [ ] Reproduzir 100% dos scores ao reexecutar o mesmo dataset com a mesma versão de metodologia.
- [ ] Preservar 100% dos assessments anteriores quando pesos ou limiares forem versionados.
- [ ] Rejeitar 100% das tentativas automatizadas de consulta cross-tenant.
- [ ] Classificar 100% das recomendações com dimensão, prioridade, evidência e ação sugerida.
- [ ] Não apresentar vulnerabilidade crítica, exposição de PII ou divergência crítica de auditoria no gate da wave.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| R-AT-001 | Assessment completo | Dataset canônico válido de um CNPJ com 100 mil transações | O diagnóstico for executado | Score geral, oito dimensões, riscos, evidências e recomendações são publicados em até 15 minutos |
| R-AT-002 | Dados insuficientes | CNPJ sem campos ou fontes necessárias para uma dimensão | O diagnóstico for executado | A dimensão perde pontos segundo regra versionada e registra as ausências como evidência |
| R-AT-003 | Reprodutibilidade | Mesmo dataset, metodologia e instante de corte lógico | O assessment for reexecutado | Scores, evidências e recomendações determinísticas são idênticos |
| R-AT-004 | Nova metodologia | Assessment anterior e nova versão de pesos aprovada | O diagnóstico for recalculado | Novo assessment referencia a nova versão e o anterior permanece consultável |
| R-AT-005 | Isolamento | Usuário de um tenant solicita assessment de outro | A API consultar o resultado | Acesso é negado e a tentativa é auditada sem revelar existência ou dados do recurso |
| R-AT-006 | Comparação temporal | Dois assessments do mesmo CNPJ em datas diferentes | O usuário solicitar evolução | A API retorna variação geral/dimensional e evidências que explicam a mudança |
| R-AT-007 | Consolidação autorizada | Escritório ou consultoria com acesso explícito a vários CNPJs | A visão consolidada for solicitada | Somente CNPJs autorizados entram no agregado e cada resultado mantém linhagem |
| R-AT-008 | Entrada não elegível | Lote em quarentena ou incompleto | O fechamento de entrada for solicitado | O assessment não é publicado como oficial e retorna pendências objetivas |
| R-AT-009 | Auditoria | Assessment publicado | Auditor consultar sua formação | Dataset, corte, metodologia, pesos, evidências, executor e timestamps são reconstruídos |

---

## Out of Scope

Explicitly NOT included in this feature:

- Calcular a obrigação tributária final de CBS/IBS ou substituir o Tax Engine da Wave 3.
- Executar split payment real ou simulado por transação.
- Projetar fluxo de caixa, capital de giro futuro ou stress tests do Digital Twin.
- Executar Shadow Tax, conciliação de quatro pontas ou reprocessamento em streaming.
- Integrar ERPs, bancos, PSPs ou Open Finance reais; a wave usa contratos e dados sintéticos da Fundação.
- Usar LLM para atribuir pontos ou alterar a metodologia oficial.
- Publicar pesos regulatórios sem aprovação humana e versionamento.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Foundation | Contratos e tenant context da Wave 1 são a única entrada aceita | Readiness não cria parser ou identidade paralela |
| Explainability | Todo ponto precisa de evidência ou ausência explícita | Agregações devem preservar linhagem até o registro de origem |
| Determinism | Mesma entrada + metodologia produz mesmo resultado | Tempo de execução e valores dinâmicos não entram na fórmula |
| Audit | Assessments publicados são imutáveis | Recalcular cria nova versão, nunca sobrescreve histórico |
| Security | Isolamento por tenant e autorização por CNPJ | Filtros e políticas são aplicados antes de agregações/consultas |
| Performance | 100 mil transações em até 15 minutos | Pipeline precisa ser incremental e particionado para a wave |
| Governance | Pesos e limiares exigem aprovação humana | Metodologia possui estado draft/approved/retired |
| Delivery | Bloqueios de JVM/CI da Fundação continuam registrados | A wave pode ser definida/desenhada, mas Ship depende dos gates herdados aplicáveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `data/databricks/`, `services/query-service/`, `contracts/`, `tests/` | Reutilizar o plano de dados e expor resultados por API tenant-scoped |
| **KB Domains** | `data-quality`, `data-modeling`, `medallion`, `lakehouse`, `lakeflow`, `testing`, `sql-patterns` | Evidências, modelagem temporal, Delta, incrementalidade e testes |
| **IaC Impact** | Modify existing / test workspace required | Precisa de catálogo/schema/pipeline de teste, sem criar nova fundação multi-cloud nesta wave |

**Why This Matters:**

- **Location** → mantém scoring fora do caminho transacional e evita novos parsers
- **KB Domains** → orienta contratos, SCD, Delta e qualidade
- **IaC Impact** → exige ambiente Databricks de teste antes do Build completo

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Transações canônicas aceitas | Avro/Delta Bronze-Silver | 100 mil no gate da wave | Após fechamento do lote | Platform data |
| Metodologia de readiness | Configuração versionada | Dezenas de regras/pesos | Por publicação aprovada | Tax governance |
| Cadastro de CNPJ e fontes | Canonical records | Um registro por entidade/versão | Conforme lote | Data quality |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `assessment_id` | UUID/STRING | NOT NULL, UNIQUE, imutável | No |
| `tenant_id` | UUID/STRING | NOT NULL, isolation key | No |
| `company_tax_id` | STRING | NOT NULL, protegido | Yes |
| `methodology_version` | STRING | NOT NULL | No |
| `cutoff_at` | TIMESTAMP_TZ | NOT NULL | No |
| `overall_score` | DECIMAL(5,2) | 0..100, NOT NULL | No |
| `dimension_scores` | ARRAY/CHILD TABLE | Exatamente oito dimensões oficiais | No |
| `evidence_count` | BIGINT | >=0 | No |
| `status` | ENUM | draft/published/invalidated | No |
| `published_at` | TIMESTAMP_TZ | Obrigatório quando published | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Silver eligibility | Até o fechamento validado da entrada | Marca de conclusão do lote |
| Readiness Gold | Até 15 minutos após fechamento para 100 mil registros | `published_at - input_closed_at` |
| Query API | Resultado publicado disponível em até 1 minuto | Primeira leitura bem-sucedida após publicação |

### Completeness Metrics

- Exatamente oito dimensões por assessment publicado.
- 100% dos impactos de score ligados a evidência ou ausência justificada.
- Zero assessment sem tenant, CNPJ, versão de metodologia ou cutoff.
- 100% dos registros de entrada contabilizados como elegíveis ou excluídos com motivo.

### Lineage Requirements

- Assessment → dimensão → regra de pontuação → evidência → registro canônico.
- Assessment → versão de metodologia → pesos/limiares → aprovadores.
- Comparação temporal deve manter IDs de ambos os assessments.
- Alteração de schema/metodologia exige análise de impacto nos consumidores.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| R-A-001 | As oito dimensões definidas cobrem o primeiro diagnóstico comercial | Exigiria nova major/minor de metodologia e dashboard | [ ] |
| R-A-002 | Especialistas conseguem aprovar pesos e limiares antes do Build final | O pipeline só poderia produzir assessment draft | [ ] |
| R-A-003 | Os dados sintéticos representam ausências e inconsistências relevantes | O score poderia parecer preciso sem cobrir falhas reais | [ ] |
| R-A-004 | Um workspace Databricks de teste estará disponível | Build fica limitado a testes locais de transformação | [ ] |
| R-A-005 | 100 mil transações são suficientes para o gate funcional desta wave | SLO e particionamento precisariam ser recalibrados | [x] |
| R-A-006 | Consolidação multi-CNPJ possui autorização explícita por relacionamento | Sem isso, visão consolidada deve permanecer desabilitada | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Diagnóstico, público e falta de evidência estão explícitos |
| Users | 3 | Cinco personas com dores específicas |
| Goals | 3 | Capacidades priorizadas e delimitadas da Wave 3+ |
| Success | 3 | Critérios quantitativos de tempo, completude, isolamento e reprodução |
| Scope | 2 | Limites claros; pesos finais dependem de aprovação especializada |
| **Total** | **14/15** | Gate mínimo atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais pesos e limiares oficiais serão aprovados para a metodologia 1.0?
- Quais evidências mínimas tornam cada dimensão elegível para publicação?
- Qual identidade/autorização representa formalmente o relacionamento consultoria/escritório ↔ CNPJ?
- Qual workspace/região Databricks será usado para o gate de 15 minutos?

As perguntas não alteram o problema ou escopo; tornam-se decisões/configurações obrigatórias no Design e riscos bloqueantes antes de Ship.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-14 | define-agent | Initial Readiness wave definition derived from master DEFINE and phased DESIGN |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_READINESS_TAXFLOW_360.md`
