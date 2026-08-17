# DEFINE: Regulatory AI e Copilot Tributário TaxFlow 360

> Ingerir legislação de fontes oficiais, indexar uma base documental/vetorial versionada e responder ou propor mudanças sempre com citações verificáveis e revisão humana.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | REGULATORY_AI_ECOSYSTEM_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Equipes fiscais precisam acompanhar normas e orientações dispersas, identificar o que mudou e avaliar impacto em regras, clientes e operações. Respostas sem origem verificável ou alterações automáticas de regras criam risco tributário, de segurança e auditoria.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Especialista fiscal | Interpreta normas e aprova regras | Gasta tempo localizando versões, vigência e dispositivos aplicáveis |
| Escritório contábil | Responde por múltiplos CNPJs | Precisa separar contexto de cada cliente e citar a fonte de toda orientação |
| Consultoria tributária | Produz análises e propostas | Precisa comparar versões e demonstrar evidências reproduzíveis |
| Product owner do motor | Mantém catálogo tributário | Precisa transformar mudança detectada em proposta governada, nunca em alteração silenciosa |
| Auditor/compliance | Reconstitui resposta e aprovação | Precisa do documento, trecho, hash, modelo, prompt, retrieval e decisão humana |
| Executivo/financeiro | Consulta impactos na empresa | Precisa de linguagem clara, incerteza explícita e ligação com simulações/digital twin |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Ingerir somente documentos provenientes de autoridades e hosts oficiais aprovados, por conectores controlados |
| **MUST** | Preservar documento original, URI canônica, autoridade, publicação, vigência, captura, hash, versão e relação de substituição |
| **MUST** | Extrair e indexar unidades citáveis por artigo, parágrafo, inciso, item, página ou seção, sem perder sua posição no original |
| **MUST** | Disponibilizar busca híbrida lexical/vetorial com filtros obrigatórios de autoridade, tipo, vigência, data de corte, jurisdição e tenant quando aplicável |
| **MUST** | Exigir em toda afirmação regulatória ao menos uma citação clicável para fonte oficial e bloquear resposta quando não houver evidência suficiente |
| **MUST** | Exibir que respostas são apoio informacional, não parecer jurídico/tributário, e representar conflito, lacuna e incerteza |
| **MUST** | Detectar mudança documental e criar `Regulatory Change Request` com diff, impacto, evidências e recomendações |
| **MUST** | Impedir Regulatory AI/Copilot de criar, aprovar, publicar ou ativar regra tributária diretamente |
| **MUST** | Submeter proposta a four-eyes com papéis separados, justificativa, testes dourados e trilha imutável |
| **MUST** | Manter isolamento multi-tenant em conversa, contexto empresarial, retrieval, cache, avaliação, logs e analytics |
| **MUST** | Proteger contra prompt injection documental, URLs não aprovadas, exfiltração, citações inventadas e uso indevido de ferramentas |
| **SHOULD** | Relacionar mudanças aprovadas a regras, simulações, Shadow Tax, Digital Twin, clientes e integrações potencialmente impactados |
| **SHOULD** | Fornecer timeline regulatória e alertas por tema, tributo, jurisdição e período |
| **COULD** | Expor Copilot para Supplier/Customer Readiness, Smart Pricing e Tax Profitability usando apenas produtos de dados autorizados |

---

## Success Criteria

- [ ] Validar origem HTTPS, host/path allowlisted e hash em 100% dos documentos publicados.
- [ ] Preservar 100% das versões documentais e detectar alteração de conteúdo quando o hash mudar.
- [ ] Obter Recall@10 mínimo de 95% e precisão de citação mínima de 98% no conjunto dourado regulatório.
- [ ] Garantir que 100% das afirmações regulatórias apresentadas tenham citação oficial resolvível e unidade citada existente no snapshot.
- [ ] Recusar 100% das perguntas regulatórias sem evidência suficiente, sem completar alíquota, vigência ou fundamento por suposição.
- [ ] Detectar 100% das mudanças inseridas no corpus sintético e criar change requests sem mutação do catálogo produtivo.
- [ ] Bloquear 100% das tentativas da IA de publicar regra ou contornar aprovação humana.
- [ ] Bloquear 100% dos testes de prompt injection, URL não aprovada, credencial em URL e retrieval cross-tenant.
- [ ] Reproduzir 100% das respostas auditadas a partir de corpus/modelo/prompt/política/data de corte versionados, ou registrar explicitamente indisponibilidade do modelo.
- [ ] Entregar p95 de busca em até 2 segundos e p95 de resposta completa em até 10 segundos no perfil sintético de 100 mil chunks.
- [ ] Vincular 100% das propostas tributárias a documento, dispositivo, diff, regra afetada e testes requeridos.
- [ ] Não apresentar vulnerabilidade crítica nem divergência crítica de segurança/auditoria no gate.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| RA-AT-001 | Ingestão oficial | Documento obtido por conector de host/path aprovado | A captura executar | Original, metadados, hash e versão imutável são armazenados |
| RA-AT-002 | URL não aprovada | URL fornecida pelo usuário ou host parecido com oficial | A ingestão for tentada | Conteúdo é rejeitado e a tentativa é auditada |
| RA-AT-003 | Nova versão | URI canônica conhecida retorna conteúdo com novo hash | A comparação executar | Nova versão e diff são criados; a anterior permanece acessível |
| RA-AT-004 | Busca vigente | Corpus contém versões passadas e futuras | Usuário consultar com data de corte | Somente evidências válidas para o cutoff e filtros entram no contexto |
| RA-AT-005 | Resposta citada | Há evidência oficial suficiente | Copilot responder | Cada afirmação regulatória possui link, documento, dispositivo e snapshot |
| RA-AT-006 | Evidência insuficiente | Retrieval não encontra suporte mínimo | Usuário pedir alíquota ou conclusão | Copilot recusa, informa lacuna e não inventa resposta/citação |
| RA-AT-007 | Fontes conflitantes | Duas fontes oficiais vigentes aparentam divergir | Copilot sintetizar | Conflito é explícito; ambas são citadas e o caso segue para especialista |
| RA-AT-008 | Prompt injection | Documento contém instrução para ignorar políticas ou revelar segredos | Pipeline/RAG processar | Texto é tratado como dado não confiável; ferramentas e segredos permanecem inacessíveis |
| RA-AT-009 | Isolamento | Conversa/contexto empresarial pertencem a outro tenant | Usuário consultar por ID conhecido | Acesso é negado sem revelar existência ou conteúdo |
| RA-AT-010 | Change request | Snapshot contém mudança relevante a uma regra | Detector avaliar impacto | Proposta draft registra diff, fontes, regras/clientes afetados e testes |
| RA-AT-011 | Publicação pela IA | Regulatory AI tenta ativar proposta | Ferramenta for chamada | Operação é tecnicamente impossível/negada e auditada |
| RA-AT-012 | Four-eyes | Autor submete proposta válida | O mesmo ator tentar aprovar | Aprovação é negada; segundo especialista autorizado é exigido |
| RA-AT-013 | Aprovação governada | Proposta tem evidência, parecer e testes dourados aprovados | Revisor diferente aprovar | Nova regra continua versionada e só é publicada pelo workflow autorizado |
| RA-AT-014 | Reprodutibilidade | Resposta auditada possui snapshot/modelo/prompt/política fixos | Avaliação de replay executar | Evidências e afirmações/citações permanecem semanticamente equivalentes |
| RA-AT-015 | Escala | Corpus sintético possui 100 mil chunks e consultas douradas | Gate de carga executar | Recall, precisão, p95 e contabilização atendem aos SLOs |
| RA-AT-016 | Fonte removida | Página oficial deixa de responder após captura validada | Usuário abrir uma resposta histórica | Snapshot/hash continuam auditáveis e indisponibilidade atual é indicada |
| RA-AT-017 | Dados empresariais | Pergunta combina legislação e métricas do tenant | Copilot consultar ferramentas | Apenas produtos autorizados são usados; resposta distingue fato legal de inferência empresarial |

---

## Out of Scope

Explicitly NOT included in this feature:

- Emitir parecer jurídico/tributário ou substituir profissional habilitado.
- Permitir que LLM, agente ou usuário sem papel publique regra tributária produtiva.
- Fazer crawling irrestrito da internet, aceitar URLs arbitrárias ou usar blogs como fundamento de cálculo.
- Tratar embedding ou resposta do modelo como fonte; a fonte é sempre o documento oficial versionado.
- Ingerir conteúdo pago/proprietário sem licença e contrato explícitos.
- Treinar modelo fundacional com dados de tenants ou compartilhar prompts/contextos entre clientes.
- Executar automaticamente pagamento, split, lançamento fiscal, alteração de ERP ou correção de documento.
- Entregar nesta primeira fatia todos os módulos complementares; Supplier/Customer Readiness, Smart Pricing e Tax Profitability serão features posteriores sobre a mesma camada governada.
- Usar dados reais sensíveis antes dos gates de segurança, privacidade e ambiente correspondentes.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Source | Apenas autoridades/hosts/paths aprovados e HTTPS | Conectores são explícitos; nenhuma URL do usuário é buscada |
| Citation | Toda afirmação regulatória exige evidência oficial | Sem citação válida, a resposta é recusada ou marcada como hipótese não regulatória |
| Temporal | Busca deve respeitar publicação, vigência, revogação e cutoff | Índice e metadados precisam ser bitemporais/versionados |
| Governance | IA somente propõe; four-eyes publica | Ferramentas do modelo não recebem permissão de escrita produtiva |
| Security | Documento recuperado é entrada não confiável | Prompt isolation, allowlist de ferramentas e validação de saída são obrigatórios |
| Tenant | Corpus público é compartilhável; contexto empresarial não | Índices, ACLs, cache e tracing distinguem conhecimento público de dados privados |
| Model | Provider/modelo pode mudar ou ficar indisponível | Gateway portável, respostas estruturadas e fallback de busca sem síntese |
| Cloud | SaaS multi-cloud AWS/Azure/GCP com Databricks | Storage/vector/model gateways usam interfaces portáveis e Terraform por provedor |
| Delivery | Waves anteriores têm gates hospedados pendentes | Wave 6 pode ser construída com dados sintéticos, mas Ship herda gates aplicáveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `contracts/`, `config/`, `services/regulatory-service/`, `data/databricks/`, `services/query-service/`, `apps/control-tower/`, `deploy/terraform/`, `tests/` | Separar captura, conhecimento, proposta transacional e experiência |
| **KB Domains** | `rag`, `vector-databases`, `llm`, `security`, `data-modeling`, `data-quality`, `lakehouse`, `testing` | Retrieval híbrido, avaliação, guardrails, temporalidade e contratos |
| **IaC Impact** | New resources / modify multi-cloud modules | Storage WORM/versionado, vector index, model gateway, queues, secrets and monitoring |

**Why This Matters:**

- **Location** → mantém corpus público, contexto tenant e workflow de regras em limites distintos.
- **KB Domains** → o Design deve selecionar chunking citável, busca híbrida, avaliação e defesa contra prompt injection.
- **IaC Impact** → a base vetorial e o gateway de modelos precisam de equivalentes governados em AWS, Azure e GCP/Databricks.

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Planalto | HTTPS oficial allowlisted | Corpus inicial sintético + snapshots aprovados | Verificação diária configurável | Regulatory governance |
| Receita Federal | HTTPS oficial allowlisted por path | Normas/orientações/tabelas selecionadas | Verificação diária configurável | Regulatory governance |
| Ministério da Fazenda | HTTPS oficial allowlisted por path | Guias/notas técnicas selecionadas | Verificação diária configurável | Regulatory governance |
| Catálogo de regras Wave 3 | YAML/Delta imutável | Centenas/milhares de versões | Por publicação | Tax governance |
| Impactos TaxFlow | Delta Gold autorizado | Regras, simulações, divergências e projeções | Conforme wave de origem | Product data owners |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `document_id` | UUID/STRING | NOT NULL, stable canonical identity | No |
| `document_version_id` | UUID/STRING | NOT NULL, immutable | No |
| `canonical_url` | STRING | HTTPS, allowlisted, no credentials/query tracking | No |
| `authority_id` | STRING | NOT NULL, approved authority | No |
| `document_type` | ENUM | NOT NULL | No |
| `published_at` | TIMESTAMP_TZ | NOT NULL when source provides | No |
| `valid_from/valid_to` | TIMESTAMP_TZ | bitemporal, nullable when unresolved | No |
| `captured_at` | TIMESTAMP_TZ | NOT NULL | No |
| `content_sha256` | CHAR(64) | NOT NULL, lowercase hex | No |
| `chunk_id` | STRING | NOT NULL, stable within version | No |
| `locator` | STRUCT | article/paragraph/item/page/section | No |
| `chunk_text` | STRING | exact normalized excerpt, immutable | No |
| `embedding_model/version` | STRING | NOT NULL for vector records | No |
| `change_request_id` | UUID/STRING | nullable, immutable workflow identity | No |
| `tenant_id` | UUID/STRING | null for public corpus; required for private context | Yes |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Capture queue | Até 24 horas após mudança observada pelo conector | source observation → capture commit |
| Search index | Até 30 minutos após snapshot validado | snapshot commit → searchable chunk |
| Change request | Até 60 minutos após diff relevante | diff commit → draft proposal |
| Copilot audit | Na mesma transação lógica da resposta | response → audit record |

### Completeness Metrics

- 100% dos documentos publicados possuem URI, autoridade, captura, hash e snapshot recuperável.
- 100% dos chunks possuem locator e referência ao documento/versionamento de origem.
- 100% das afirmações regulatórias possuem citation IDs validados contra chunks recuperados.
- 100% das propostas registram diff, evidência e impacto; 0 publicação direta pela IA.
- 100% das respostas e avaliações recebem disposição: answered, refused, conflicted ou failed com motivo.

### Lineage Requirements

- Resposta → afirmação → citação → chunk → snapshot/hash → URI/autoridade oficial.
- Retrieval → consulta normalizada → filtros/cutoff → ranking lexical/vetorial → versões do índice/embedding.
- Proposta → diff documental → dispositivos → regra atual → casos dourados/impactos → aprovação humana.
- Conversa → tenant/ator/papel → modelo/prompt/política/ferramentas → resposta/recusa.
- Documento → captura/conector → validações → transformação/chunking → índice e avaliações.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| RA-A-001 | Autoridades iniciais permitem captura dos documentos selecionados dentro de seus termos e limites | Será necessário acordo/API/processo manual de publicação | [ ] |
| RA-A-002 | Artigo/parágrafo/inciso/página são localizadores suficientes para o corpus inicial | Chunking precisará de adaptadores por formato documental | [ ] |
| RA-A-003 | Busca híbrida em índice Databricks/adapter portável atende 100 mil chunks | Será necessário serviço vetorial dedicado por edição | [ ] |
| RA-A-004 | Especialistas fornecerão conjunto dourado de perguntas, citações e mudanças | Ship ficará bloqueado por ausência de avaliação jurídica/fiscal | [ ] |
| RA-A-005 | Um gateway LLM empresarial com no-training/retention controls estará disponível | Primeira versão operará busca citada sem síntese generativa | [ ] |
| RA-A-006 | Corpus público pode ser compartilhado entre tenants | Será necessário índice físico separado por tenant/região | [ ] |
| RA-A-007 | Links oficiais e snapshots Wave 3 continuam imutáveis | Migração de provenance será necessária | [x] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Monitoramento, confiança e risco de alteração automática estão explícitos |
| Users | 3 | Usuários fiscais, operacionais, executivos e auditoria identificados |
| Goals | 3 | Ingestão, RAG citado, propostas, governança e segurança priorizados |
| Success | 3 | Recall, precisão, recusa, isolamento, reprodução e performance mensuráveis |
| Scope | 2 | Fronteira clara; fornecedores finais de vector/model gateway dependem do Design |
| **Total** | **14/15** | Gate mínimo atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais autoridades, coleções e tipos documentais entram na primeira allowlist além das três já aprovadas?
- Qual serviço de vector search será padrão SaaS e quais adapters serão exigidos nas edições dedicadas AWS/Azure/GCP?
- Qual gateway/provedor LLM cumpre residência, retenção, no-training, auditoria e fallback exigidos?
- Quais especialistas e papéis podem classificar conflito, aprovar change request e liberar regra?
- Qual conjunto dourado oficial validará recall, citações, interpretação temporal e impacto?

Essas decisões selecionam adapters e gates no Design sem flexibilizar fonte oficial, citação obrigatória ou revisão humana.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | define-agent | Definição inicial da Wave 6 Regulatory AI, base vetorial governada e Copilot citado |
| 1.1 | 2026-08-17 | design-agent | Design técnico concluído e liberado para Build |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_REGULATORY_AI_ECOSYSTEM_TAXFLOW_360.md`
