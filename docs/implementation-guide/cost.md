# Custos Estimados

Estimativa de custos mensais para a infraestrutura AWS da Plataforma Cognitiva (região us-east-1).

## Componentes

| Recurso | Tipo | Custo Estimado/mês |
|---------|------|-------------------|
| EC2 | t3.medium (2 vCPU, 4GB RAM) | ~$30.37 |
| EBS | 30 GB gp3 | ~$2.40 |
| RDS PostgreSQL | db.t3.micro (2 vCPU, 1GB RAM) | ~$12.41 |
| RDS Storage | 20 GB gp2 | ~$2.30 |
| S3 | Bucket para frontend (< 1GB) | ~$0.02 |
| Data Transfer | Estimado 10GB/mês | ~$0.90 |

## Total Estimado

**~$48.40/mês** (sem free tier)

## Observações

- Com Free Tier (12 primeiros meses): EC2 t2.micro e RDS db.t3.micro são gratuitos por 750h/mês
- O t3.medium foi escolhido por necessidade de memória para carregar o modelo LLM (SmolLM2-360M)
- Para reduzir custos em produção, considere Reserved Instances ou Savings Plans
- O custo de transferência de dados pode variar conforme o uso
