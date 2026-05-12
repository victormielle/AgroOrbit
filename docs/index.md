# Plataforma Cognitiva - Guia de Implementação

Bem-vindo ao guia de implementação da **Plataforma Cognitiva**! Esta é uma API RESTful de busca semântica e chat com IA, construída com Flask, PostgreSQL/pgvector e modelos de linguagem locais.

## Visão Geral

A plataforma permite:

- **Upload de documentos** (PDF e texto) com indexação vetorial automática
- **Busca semântica** por similaridade usando embeddings (all-MiniLM-L6-v2)
- **Chat com IA** usando RAG (Retrieval-Augmented Generation) com LLM local (SmolLM2-360M)
- **Listagem de documentos** indexados

## Stack Tecnológica

| Componente | Tecnologia |
|-----------|-----------|
| API | Flask (Python 3.11) |
| Banco de Dados | PostgreSQL 15 + pgvector |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| LLM | HuggingFace SmolLM2-360M-Instruct |
| Infraestrutura | AWS (EC2 + RDS + S3) |
| Frontend | HTML/JS estático (S3) |

## Arquitetura

Veja a [visão geral da arquitetura](implementation-guide/architecture.md) para entender como os componentes se conectam.

## Começando

1. [Como criar EC2 Ubuntu](implementation-guide/tutorials/criar-ec2.md)
2. [Como criar RDS PostgreSQL com pgvector](implementation-guide/tutorials/criar-RDS.md)
3. [Como conectar EC2 ao RDS](implementation-guide/tutorials/conectar-ec2-rds.md)
4. [Como criar Bucket S3](implementation-guide/tutorials/criar-bucket-s3.md)
5. [Como criar site no S3](implementation-guide/tutorials/criar-site-s3.md)
6. [Deploy da API](implementation-guide/deployment.md)
