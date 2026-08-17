# DEFINE: Simulador Tributário TaxFlow 360

> Comparar, de forma determinística e auditável, o regime atual com cenários temporais de CBS/IBS e split payment usando operações sintéticas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | TAX_SIMULATION_TAXFLOW_360 |
| **Date** | 2026-08-15 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Equipes fiscais e financeiras, escritórios contábeis, consultorias e instituições de pagamento não conseguem comparar antecipadamente o resultado tributário e financeiro de uma operação no regime atual, na transição CBS/IBS e com split payment, preservando regra, vigência, fundamento, memória de cálculo e efeitos sobre o valor líquido da empresa.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Equipe fiscal | Valida classificação, incidência, créditos e apuração | Não consegue explicar por que os cenários produzem valores diferentes |
| Equipe financeira/CFO | Avalia caixa, margem e necessidade de liquidez | Não enxerga quanto e quando o split reduz o caixa disponível |
| Escritório contábil | Simula vários CNPJs | Precisa aplicar regras consistentes sem misturar clientes ou resultados |
| Consultoria tributária | Recomenda estratégias de transição | Precisa de cenários reproduzíveis e defensáveis perante o cliente |
| Banco, fintech ou PSP | Avalia instruções e liquidação de split | Precisa validar somas, parcelas, estornos e devoluções antes da integração real |
| Auditor/aprovador | Governa regras tributárias | Precisa reconstruir entrada, regra, aprovação, cálculo e resultado |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Simular a mesma operação nos cenários `current`, `cbs_ibs_transition` e `cbs_ibs_split` sem alterar lançamentos reais |
| **MUST** | Selecionar somente regras aprovadas e vigentes na data da operação, com versionamento e four-eyes |
| **MUST** | Produzir CBS, IBS, tributos do regime atual, créditos elegíveis, valor destinado ao Fisco, valor líquido da empresa e deltas entre cenários |
| **MUST** | Preservar memória de cálculo completa: base, alíquota, redução, regra, vigência, arredondamento, fundamento e evidências de entrada |
| **MUST** | Exibir em toda resposta tributária ao menos um link clicável para a fonte oficial que fundamenta cada regra aplicada |
| **MUST** | Garantir idempotência, isolamento por tenant/CNPJ e imutabilidade de simulações publicadas |
| **MUST** | Simular split por pagamento/parcela e preservar a soma entre Fisco, empresa, estorno e devolução |
| **SHOULD** | Executar cenários unitários via API e lotes analíticos no Databricks com paridade de resultado |
| **SHOULD** | Comparar versões de regra e explicar cada mudança de valor por componente tributário |
| **COULD** | Permitir cenários hipotéticos privados com alíquotas parametrizadas, claramente marcados como não oficiais |

---

## Success Criteria

- [ ] Obter 100% de correspondência com os valores e memórias esperados em um conjunto dourado com pelo menos 50 casos representativos.
- [ ] Reproduzir 100% dos resultados para a mesma entrada, data de corte, catálogo de regras e chave idempotente.
- [ ] Rejeitar 100% das regras não aprovadas, fora de vigência ou incompatíveis com o tenant.
- [ ] Preservar a equação financeira do split em 100% dos testes, sem diferença superior a `R$ 0,01` decorrente de arredondamento distribuído.
- [ ] Processar uma simulação unitária com p95 de até 500 ms no gate controlado, excluindo autenticação externa e cold start.
- [ ] Processar 100 mil operações sintéticas em até 15 minutos no ambiente Databricks da wave.
- [ ] Manter paridade de 100% entre o motor transacional e o lote analítico para o conjunto dourado.
- [ ] Explicar 100% dos valores e deltas com regra, versão, vigência, fórmula, entradas e arredondamento.
- [ ] Publicar 0 respostas tributárias ou simulações oficiais sem `source_url`, órgão emissor, identificador do documento e instante de captura verificáveis.
- [ ] Bloquear 100% das consultas e execuções cross-tenant automatizadas.
- [ ] Não apresentar vulnerabilidade crítica nem divergência crítica de segurança ou auditoria no gate da wave.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| TS-AT-001 | Comparação completa | Operação dourada e regras aprovadas dos três cenários | A simulação for executada | Os três resultados, deltas e memórias correspondem ao ground truth |
| TS-AT-002 | Regra fora de vigência | Operação anterior ou posterior à vigência | O motor selecionar regras | A regra inválida não é aplicada e a decisão é explicada |
| TS-AT-003 | Regra sem aprovação | Regra em `draft` ou aprovada por uma só pessoa | Uma simulação oficial for solicitada | A execução oficial é rejeitada sem alterar resultados anteriores |
| TS-AT-004 | Split simples | Venda com um pagamento e tributos calculados | O split for simulado | Fisco + empresa equivalem ao valor liquidado segundo a precisão monetária definida |
| TS-AT-005 | Parcelamento | Venda com múltiplas parcelas e resíduo de centavos | O split for distribuído | Todas as parcelas fecham e o resíduo é atribuído deterministicamente |
| TS-AT-006 | Estorno/devolução | Split simulado previamente e evento total ou parcial | O ajuste for processado | Componentes são revertidos proporcionalmente, sem exceder o original |
| TS-AT-007 | Idempotência | Mesma requisição e chave entregues repetidamente | O motor processar as tentativas | Um único resultado imutável é produzido e as duplicatas são auditadas |
| TS-AT-008 | Memória de cálculo | Resultado publicado | Um auditor consultar sua formação | Entrada, fórmulas, regras, fundamento, arredondamento e aprovações são reconstruídos |
| TS-AT-009 | Isolamento | Usuário de outro tenant usa um ID conhecido | A API executar ou consultar | Acesso é negado sem revelar dados ou existência do recurso |
| TS-AT-010 | Paridade batch/API | Mesmo conjunto dourado e mesmo catálogo | Motores Kotlin e Databricks executarem | Valores monetários, decisões e rule IDs são idênticos |
| TS-AT-011 | Regra alterada | Simulação publicada e nova versão aprovada | A operação for recalculada | Nova simulação referencia a nova regra e a anterior permanece consultável |
| TS-AT-012 | Entrada inelegível | Operação em quarentena ou sem campos obrigatórios | A simulação for solicitada | Nenhum resultado oficial é publicado e as pendências são estruturadas |
| TS-AT-013 | Fonte oficial obrigatória | Regra sem URL oficial ou com URL fora da lista de autoridades permitidas | A publicação ou resposta oficial for solicitada | A operação é bloqueada e retorna a pendência de proveniência |
| TS-AT-014 | Citação navegável | Cálculo baseado em uma ou mais regras aprovadas | A API ou interface apresentar o resultado | Cada regra possui link clicável, documento, dispositivo, versão e data de consulta |

---

## Out of Scope

Explicitly NOT included in this feature:

- Movimentar, custodiar, liquidar ou recolher recursos reais.
- Substituir apuração oficial, obrigação acessória ou opinião jurídico-tributária.
- Publicar automaticamente regra extraída por IA ou fonte regulatória sem aprovação humana.
- Projetar fluxo de caixa e capital de giro completo; isso pertence ao Digital Twin da Wave 4.
- Executar Shadow Tax contínuo, conciliação de quatro pontas ou tratamento operacional de divergências.
- Integrar ambientes reais de Receita, CGIBS, bancos, adquirentes, PSPs ou ERPs nesta wave.
- Cobrir todos os regimes, exceções e setores brasileiros antes da validação do catálogo dourado inicial.
- Usar dados fiscais, bancários ou pessoais reais; os gates usam dados sintéticos.
- Ingerir e interpretar automaticamente toda a legislação ou operar busca vetorial; a Wave 3 consome fontes oficiais cadastradas e aprovadas, enquanto a base documental/vetorial pertence à Wave 6.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Regulatory | Regras e especificações podem mudar durante a transição | Toda regra precisa de versão, vigência, fonte e aprovação |
| Determinism | Mesma entrada e catálogo devem produzir o mesmo resultado | Datas implícitas, `float` e dependências externas não entram no cálculo |
| Monetary | Valores monetários exigem precisão decimal | Escala, modo de arredondamento e distribuição de resíduo são parte do contrato |
| Security | Tenant e CNPJ delimitam execução, regra e leitura | Autorização ocorre antes do cálculo e da consulta |
| Audit | Resultados oficiais são imutáveis | Correção ou nova regra gera uma nova simulação vinculada |
| Provenance | Toda resposta tributária precisa apontar sua origem oficial | Regra sem URL, documento, dispositivo, hash e captura não pode ser publicada |
| Architecture | Tax Engine deve permanecer cloud-agnostic | Core Kotlin não depende de SDK específico de AWS, Azure ou GCP |
| Data | Somente contratos canônicos aceitos entram no cálculo oficial | Registros em quarentena ficam fora e recebem motivo |
| Delivery | Gates externos de Foundation/Readiness continuam abertos | A wave pode ser definida e desenhada; Ship depende dos gates herdados aplicáveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `services/tax-service/`, `services/payment-service/`, `services/query-service/`, `contracts/`, `config/`, `data/databricks/`, `apps/control-tower/`, `tests/` | Reusar os motores e contratos existentes, sem criar um core paralelo |
| **KB Domains** | `data-modeling`, `data-quality`, `spark`, `lakehouse`, `sql-patterns`, `testing` | Contratos temporais, precisão, paridade, incrementalidade e qualidade |
| **IaC Impact** | Modify existing / test workspace required | Novos jobs/tabelas de simulação no bundle existente; sem nova fundação multi-cloud |

**Why This Matters:**

- **Location** → mantém o cálculo transacional independente da cloud e o lote no lakehouse
- **KB Domains** → orienta contratos, temporalidade, precisão, paridade e testes dourados
- **IaC Impact** → explicita o workspace Databricks necessário para validar o SLO em lote

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Operações canônicas aceitas | Avro/Delta/API | 100 mil no gate da wave | Após fechamento ou por requisição | Platform data |
| Catálogo de regras aprovado | PostgreSQL/YAML snapshot | Centenas de regras/versionamentos | Por publicação four-eyes | Tax governance |
| Pagamentos e parcelas sintéticos | Evento/Delta | Até uma relação N:1 por operação | Mesmo lote/correlação | Payment domain |
| Parâmetros de cenário | API/config versionada | Um conjunto por simulação | No instante da solicitação | Fiscal/Finance |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `simulation_id` | UUID/STRING | NOT NULL, UNIQUE, imutável | No |
| `tenant_id` | UUID/STRING | NOT NULL, isolation key | No |
| `company_tax_id` | STRING | NOT NULL, protegido | Yes |
| `operation_id` | STRING | NOT NULL, lineage key | Potentially |
| `scenario_type` | ENUM | current/transition/split | No |
| `rule_set_version` | STRING | NOT NULL | No |
| `effective_at` | TIMESTAMP_TZ | NOT NULL | No |
| `gross_amount` | DECIMAL(19,4) | >= 0 | No |
| `current_tax_amount` | DECIMAL(19,4) | >= 0 | No |
| `cbs_amount` | DECIMAL(19,4) | >= 0 | No |
| `ibs_amount` | DECIMAL(19,4) | >= 0 | No |
| `tax_authority_amount` | DECIMAL(19,4) | >= 0 | No |
| `company_net_amount` | DECIMAL(19,4) | NOT NULL | No |
| `calculation_memory` | ARRAY/JSON | NOT NULL, rule/evidence lineage | No |
| `legal_sources` | ARRAY/JSON | NOT NULL, ao menos uma fonte oficial por regra | No |
| `status` | ENUM | draft/published/invalidated | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Unitário/API | p95 ≤ 500 ms no gate controlado | Request start → response end |
| Batch Gold | ≤ 15 minutos para 100 mil operações | `published_at - input_closed_at` |
| Query | Resultado publicado disponível em ≤ 1 minuto | Primeira leitura autorizada |

### Completeness Metrics

- 100% das simulações oficiais possuem tenant, CNPJ, operação, cenário, regra e vigência.
- 100% dos componentes monetários possuem escala e modo de arredondamento explícitos.
- 100% dos valores calculados possuem passos de memória e regra de origem.
- 100% das respostas tributárias possuem links oficiais navegáveis e metadados de proveniência.
- 100% das entradas são contabilizadas como calculadas ou rejeitadas com motivo.
- Zero resultado oficial baseado em regra não aprovada ou entrada em quarentena.

### Lineage Requirements

- Simulação → cenário → operação → documento/pagamento/parcela canônicos.
- Componente tributário → passo de cálculo → regra/versionamento/vigência/fundamento/aprovadores.
- Regra → URL oficial → órgão emissor → documento/dispositivo → data de publicação/captura → hash do conteúdo.
- Split → componente devido → instrução simulada → parcela/estorno/devolução.
- Comparação → IDs imutáveis dos cenários e regra usada em cada lado.
- Mudança de regra ou schema exige análise de impacto nos resultados históricos e consumidores.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| TS-A-001 | Especialistas fornecerão e aprovarão um conjunto dourado inicial de regras e resultados | Acurácia jurídico-tributária não poderá ser certificada | [ ] |
| TS-A-002 | O catálogo inicial cobre casos suficientes para validar a arquitetura, não todo o sistema tributário | Escopo e cronograma aumentariam substancialmente | [ ] |
| TS-A-003 | `Decimal(19,4)` e arredondamento monetário configurado atendem aos casos iniciais | Contratos e golden cases precisariam de nova versão | [ ] |
| TS-A-004 | Eventos sintéticos representam parcelas, estornos e devoluções relevantes | O split poderia passar sem cobrir exceções operacionais | [ ] |
| TS-A-005 | Um workspace Databricks estará disponível para paridade e SLO de lote | Build ficará restrito a validações locais/estáticas | [ ] |
| TS-A-006 | O core existente suporta extensão sem dependência de cloud | Poderá ser necessária refatoração antes do Design final | [x] |
| TS-A-007 | Simulação não precisa chamar sistemas governamentais ou financeiros reais | Integrações, autorizações e riscos ampliariam a wave | [x] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Dor, personas e impacto tributário-financeiro estão explícitos |
| Users | 3 | Seis papéis e suas necessidades foram identificados |
| Goals | 3 | Cenários, governança, memória, split e paridade estão priorizados |
| Success | 3 | Acurácia, latência, lote, isolamento e auditabilidade são mensuráveis |
| Scope | 2 | Limites claros; o catálogo dourado depende de validação especializada |
| **Total** | **14/15** | Gate mínimo atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais operações, regimes, exceções, alíquotas e fundamentos compõem a versão 1.0 do conjunto dourado?
- Qual escala e política oficial de arredondamento serão aprovadas por componente e por parcela?
- Quais campos tornam uma operação elegível em cada cenário?
- Qual allowlist inicial de domínios e autoridades oficiais será aceita para publicação de regras?
- Qual ambiente controlado medirá p95 do core e SLO do Databricks?

Essas perguntas são decisões governadas e gates de Build/Ship; não alteram a fronteira funcional da wave.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-15 | define-agent | Definição inicial da Wave 3 derivada do DEFINE e DESIGN mestres |
| 1.1 | 2026-08-15 | iterate-agent | Tornou links oficiais e metadados de proveniência obrigatórios; ingestão vetorial permanece na Wave 6 |
| 1.2 | 2026-08-15 | design-agent | Design técnico concluído com catálogo aprovado, citações obrigatórias e paridade batch/API |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_TAX_SIMULATION_TAXFLOW_360.md`
