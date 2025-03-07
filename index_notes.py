import os
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import json
import datetime
import re
import yaml
from config import *

# Carrega variáveis de ambiente
load_dotenv()

# Arquivo para armazenar informações sobre arquivos processados
PROCESSED_FILES_DB = os.path.join(CHROMA_PERSIST_DIR, "processed_files.json")

def get_markdown_files(vault_path: str) -> List[Path]:
    """Retorna uma lista de todos os arquivos .md no vault."""
    vault_path = Path(vault_path)
    return list(vault_path.rglob("*.md"))

def read_markdown_file(file_path: Path) -> str:
    """Lê o conteúdo de um arquivo markdown."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return ""

def extract_frontmatter(content: str) -> Dict:
    """Extrai o YAML frontmatter de uma nota do Obsidian."""
    frontmatter = {}
    # Procura pelo padrão de frontmatter (entre --- no início do arquivo)
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Extrai o conteúdo entre os marcadores ---
        frontmatter_text = match.group(1)
        try:
            # Tenta fazer o parse como YAML
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except Exception as e:
            print(f"Erro ao analisar frontmatter: {e}")
    
    return frontmatter

def extract_metadata(file_path: Path, content: str) -> Dict:
    """Extrai todos os metadados relevantes de uma nota."""
    # Obtém informações básicas do sistema de arquivos
    stat = os.stat(file_path)
    created_time = stat.st_ctime
    modified_time = stat.st_mtime
    
    # Converte timestamps para formato legível
    created_str = datetime.datetime.fromtimestamp(created_time).isoformat()
    modified_str = datetime.datetime.fromtimestamp(modified_time).isoformat()
    
    # Extrai o YAML frontmatter se existir
    frontmatter = extract_frontmatter(content)
    
    # Cria o dicionário de metadados
    metadata = {
        "source": str(file_path.relative_to(OBSIDIAN_VAULT_PATH)),
        "created_at": created_str,
        "modified_at": modified_str,
        "filename": file_path.name,
        "file_path": str(file_path.relative_to(OBSIDIAN_VAULT_PATH)),
    }
    
    # Adiciona valores do frontmatter, se existirem
    if frontmatter:
        # Adiciona tags do frontmatter, convertendo para lista se necessário
        if "tags" in frontmatter:
            if isinstance(frontmatter["tags"], list):
                metadata["tags"] = frontmatter["tags"]
            else:
                metadata["tags"] = [frontmatter["tags"]]
        
        # Adiciona outros campos do frontmatter que possam ser úteis
        for key in ["title", "date", "created", "modified", "category", "aliases"]:
            if key in frontmatter:
                metadata[key] = frontmatter[key]
    
    return metadata

def load_processed_files() -> Dict:
    """Carrega o registro de arquivos processados."""
    if not os.path.exists(PROCESSED_FILES_DB):
        return {}
    
    try:
        with open(PROCESSED_FILES_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar registro de arquivos processados: {e}")
        return {}

def save_processed_files(processed_files: Dict):
    """Salva o registro de arquivos processados."""
    os.makedirs(os.path.dirname(PROCESSED_FILES_DB), exist_ok=True)
    
    try:
        with open(PROCESSED_FILES_DB, 'w', encoding='utf-8') as f:
            json.dump(processed_files, f, indent=2)
    except Exception as e:
        print(f"Erro ao salvar registro de arquivos processados: {e}")

def main():
    # Inicializa o ChromaDB
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=EMBEDDING_MODEL
    )
    
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    
    # Cria ou obtém a coleção
    collection = client.get_or_create_collection(
        name="obsidian_notes",
        embedding_function=openai_ef
    )
    
    # Carrega o registro de arquivos processados
    processed_files = load_processed_files()
    
    # Obtém todos os arquivos markdown
    md_files = get_markdown_files(OBSIDIAN_VAULT_PATH)
    print(f"Encontrados {len(md_files)} arquivos markdown")
    
    # Contador para novas notas e notas atualizadas
    new_count = 0
    updated_count = 0
    
    # Processa cada arquivo
    for file_path in md_files:
        # Usa o caminho relativo como ID do documento
        doc_id = str(file_path.relative_to(OBSIDIAN_VAULT_PATH))
        
        # Verifica se o arquivo precisa ser processado
        mtime = os.path.getmtime(file_path)
        mtime_str = datetime.datetime.fromtimestamp(mtime).isoformat()
        
        # Se o arquivo já foi processado e não foi modificado, pula
        if doc_id in processed_files and processed_files[doc_id] == mtime_str:
            continue
        
        # Lê o conteúdo do arquivo
        content = read_markdown_file(file_path)
        if not content:
            continue
        
        # Extrai os metadados completos
        metadata = extract_metadata(file_path, content)
            
        # Adiciona ou atualiza o documento na coleção
        collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        # Atualiza o registro de arquivos processados
        if doc_id in processed_files:
            updated_count += 1
            print(f"Atualizado: {doc_id}")
        else:
            new_count += 1
            print(f"Novo: {doc_id}")
            
        processed_files[doc_id] = mtime_str
    
    # Salva o registro atualizado
    save_processed_files(processed_files)
    
    print(f"Indexação concluída: {new_count} novos arquivos, {updated_count} arquivos atualizados")

if __name__ == "__main__":
    main() 