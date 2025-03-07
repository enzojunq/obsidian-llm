# Obsidian Notes Search

Este projeto permite buscar e consultar suas notas do Obsidian usando LLMs (Large Language Models) e embeddings.

## Configuração

1. Clone este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com sua chave da API OpenAI:

```
OPENAI_API_KEY=sua_chave_aqui
```

4. Configure o caminho do seu vault do Obsidian no arquivo `config.py`

## Uso

1. Primeiro, indexe suas notas:

```bash
python index_notes.py
```

2. Para fazer consultas:

```bash
python query.py "sua pergunta aqui"
```

## Como funciona

O sistema usa o seguinte fluxo:

1. Lê todas as notas .md do seu vault Obsidian
2. Cria embeddings usando o modelo da OpenAI
3. Armazena os embeddings em uma base ChromaDB
4. Usa RAG (Retrieval Augmented Generation) para responder às consultas
