import os
from pathlib import Path

# Caminhos para as notas
OBSIDIAN_VAULT_PATH = str(Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "2025")
APPLE_NOTES_PATH = str(Path.home() / "Library" / "Group Containers" / "group.com.apple.notes")

# Configurações de fontes de notas
SOURCES = {
    "obsidian": True,  # True para habilitar busca em notas do Obsidian
    "apple_notes": True  # True para habilitar busca em notas do Apple Notes
}

# Configurações do ChromaDB
CHROMA_PERSIST_DIR = "chroma_db"

# Configurações do OpenAI
EMBEDDING_MODEL = "text-embedding-3-small"
COMPLETION_MODEL = "gpt-4o-mini"

# Número máximo de chunks para usar no contexto
MAX_CHUNKS = 5 