# Considerações

## Segurança

- O Security Group do RDS deve permitir acesso **apenas** a partir do Security Group da EC2
- Nunca exponha o RDS publicamente em produção
- Use variáveis de ambiente (`.env`) para credenciais — nunca commite senhas no repositório
- Habilite SSL/TLS nas conexões com o banco de dados

## Performance

- O modelo de embeddings (all-MiniLM-L6-v2) gera vetores de 384 dimensões
- O LLM (SmolLM2-360M) requer ~1.5GB de RAM — por isso usamos t3.medium
- Para documentos grandes, o chunking (500 caracteres com overlap de 50) garante granularidade na busca
- O pgvector usa índice IVFFlat ou HNSW para buscas vetoriais eficientes em escala

## Escalabilidade

- Para maior carga, considere usar Gunicorn com múltiplos workers
- O RDS pode ser escalado verticalmente (instância maior) ou com Read Replicas
- Para alta disponibilidade, configure Multi-AZ no RDS

## Limitações

- O LLM local (SmolLM2-360M) é compacto e pode gerar respostas limitadas
- Para respostas mais sofisticadas, considere migrar para Amazon Bedrock (Nível 3 de maturidade)
- O upload de PDFs muito grandes pode causar timeout — considere processamento assíncrono
