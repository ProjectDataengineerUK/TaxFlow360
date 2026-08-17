# Contexto de sistema

## Limites

O TaxFlow 360 recebe operações fiscais e financeiras, normaliza os dados, calcula cenários tributários, simula split payment, projeta caixa e compara o regime atual com regras futuras. Sistemas externos continuam responsáveis pela emissão fiscal, movimentação bancária e escrituração oficial.

```text
ERP/PDV/E-commerce/Bancos
            |
            v
     TaxFlow Transaction Plane
            |
            v
       Kafka contracts
            |
            v
     Databricks Data Plane
            |
            v
       APIs/Dashboards
```

## Regras de dependência

1. Serviços implantáveis não importam código uns dos outros.
2. Integrações síncronas usam OpenAPI; assíncronas usam Avro.
3. O plano analítico não participa do cálculo crítico da venda.
4. Adaptadores cloud não contêm regras tributárias.
5. Eventos são imutáveis, versionados e reprocessáveis.

## Ondas

1. Contratos, tenancy, auditoria e dados sintéticos.
2. Diagnóstico e Tax Readiness Score.
3. Simulação tributária e split.
4. Digital Twin financeiro.
5. Shadow Tax e conciliação.
6. Regulatory AI e módulos complementares.

