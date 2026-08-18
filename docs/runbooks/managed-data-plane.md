# Managed data plane AWS

O adapter AWS declara Aurora PostgreSQL, MSK Kafka, ElastiCache Redis e CloudWatch. Os três serviços de dados são opt-in:

```hcl
enable_managed_data_plane = true
private_subnet_ids        = ["subnet-private-a", "subnet-private-b", "subnet-private-c"]
data_security_group_id    = "sg-workload-only"
```

Requisitos do ambiente protegido:

- subnets privadas em pelo menos duas zonas;
- security group sem entrada pública, limitado aos workloads autorizados;
- identidade de workload para Terraform e rotação de chaves KMS;
- orçamento e janela de manutenção aprovados;
- backup, restauração e retenção revisados pelo responsável de segurança.

O padrão permanece `enable_managed_data_plane = false`. Em desenvolvimento são permitidos somente:

```powershell
terraform fmt -check -recursive deploy/terraform
terraform -chdir=deploy/terraform/aws init -backend=false
terraform -chdir=deploy/terraform/aws validate
```

`plan`, `apply`, `destroy` e credenciais não fazem parte do fluxo local. Aurora é a fonte transacional; Redis é apenas cache; MSK usa TLS, replicação 3, `min.insync.replicas=2` e criação automática de tópicos desabilitada. Logs de aplicação têm retenção de 30 dias e auditoria 2.555 dias, ambos com KMS.

Origens oficiais: [Amazon Aurora PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Updates.html), [Amazon MSK](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html), [Amazon ElastiCache for Redis](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html) e [CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html).
