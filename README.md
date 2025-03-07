# Obsidian-LLM - Assistente Inteligente para suas Notas do Obsidian

Este projeto cria um poderoso assistente de notas baseado em IA que permite consultar suas notas do Obsidian usando LLMs (Large Language Models) e embeddings vetoriais.

## Recursos

- **Processamento inteligente de metadados**: Extrai e utiliza metadados como data de criação, tags, e YAML frontmatter
- **Indexação incremental**: Processa apenas notas novas ou modificadas em execuções subsequentes
- **Interface conversacional**: Mantém o contexto durante a conversa para interações naturais
- **Busca semântica**: Encontra informações relevantes mesmo quando as palavras-chave exatas não aparecem na consulta

## Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Uma chave de API OpenAI

### Instalação

1. Clone este repositório

```bash
git clone https://github.com/seu-usuario/obsidian-llm.git
cd obsidian-llm
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com sua chave da API OpenAI:

```
OPENAI_API_KEY=sua_chave_aqui
```

4. Configure o projeto no arquivo `config.py`:

```python
# Caminho para o vault do Obsidian
OBSIDIAN_VAULT_PATH = "caminho/para/seu/vault/obsidian"  # Ajuste para seu sistema

# Configurações de modelos
EMBEDDING_MODEL = "text-embedding-3-small"
COMPLETION_MODEL = "gpt-4o-mini"  # Ou outro modelo de sua preferência

# Número máximo de chunks retornados nas buscas
MAX_CHUNKS = 5
```

## Uso

### Indexando suas notas

Execute o script de indexação para processar suas notas e criar os embeddings:

```bash
python index_notes.py
```

Este script pode ser executado periodicamente (por exemplo, diariamente) para manter seu índice atualizado. A indexação é incremental e processará apenas notas novas ou modificadas.

### Consultando suas notas

Para iniciar uma sessão de conversa com o assistente:

```bash
python query.py
```

Durante a sessão:

- Digite suas perguntas normalmente
- Digite `clear` para limpar o histórico da conversa
- Digite `exit` ou `quit` para sair

### Exemplos de perguntas

- "Qual o resumo das minhas notas sobre machine learning?"
- "Quando foi a última vez que escrevi sobre viagens?"
- "Quais projetos eu estava planejando no mês passado?"
- "Encontre todas as minhas notas sobre receitas vegetarianas"
- "Em que dia eu mencionei sentir muita alegria?"

## Como funciona

O sistema usa o seguinte fluxo:

1. **Indexação**:

   - Lê notas do Obsidian (.md)
   - Extrai metadados (datas, tags, frontmatter YAML, etc.)
   - Gera embeddings usando o modelo da OpenAI
   - Armazena dados em uma base ChromaDB persistente
   - Rastreia arquivos processados para evitar reindexação desnecessária

2. **Busca**:

   - Converte sua pergunta em um embedding
   - Encontra as notas mais semelhantes semanticamente
   - Agrupa os resultados com seus metadados como contexto

3. **Resposta**:
   - Usa uma LLM (por padrão GPT-4o-mini) para gerar respostas baseadas no contexto
   - Mantém o histórico da conversa para permitir perguntas de acompanhamento

## Personalização

Você pode personalizar vários aspectos do sistema no arquivo `config.py`:

- Modelos de embedding e completion da OpenAI
- Número de chunks retornados nas buscas

## Requisitos técnicos

- Python 3.8+
- OpenAI API
- Bibliotecas Python: chromadb, openai, pyyaml, python-dotenv e suas dependências

## Agendamento automático

Para manter seu índice atualizado automaticamente:

### macOS (usando LaunchAgent):

1. Crie um arquivo plist em `~/Library/LaunchAgents/com.seu-usuario.indexnotas.plist`
2. Configure-o para executar diariamente o script de indexação

### Linux/macOS (usando Cron):

```bash
# Edite seu crontab (executa às 9h todos os dias)
crontab -e

# Adicione esta linha:
0 9 * * * cd /caminho/completo/para/projeto && python3 index_notes.py
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
