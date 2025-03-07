import os
import sys
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from config import *

# Carrega variáveis de ambiente
load_dotenv()

def format_metadata(metadata: dict) -> str:
    """Formata os metadados de uma nota para inclusão no contexto."""
    # Filtra os metadados mais relevantes
    relevant_keys = ["created_at", "modified_at", "tags", "title", "date", "category", "aliases"]
    
    # Formata cada metadado presente
    formatted_parts = []
    for key in relevant_keys:
        if key in metadata and metadata[key]:
            value = metadata[key]
            # Formata listas como strings separadas por vírgula
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            formatted_parts.append(f"{key}: {value}")
    
    # Retorna os metadados formatados
    if formatted_parts:
        return "Metadados:\n" + "\n".join(formatted_parts)
    return ""

def get_relevant_context(query: str, collection) -> str:
    """Recupera os documentos mais relevantes para a consulta."""
    results = collection.query(
        query_texts=[query],
        n_results=MAX_CHUNKS,
        include=["documents", "metadatas"]
    )
    
    # Combina os documentos recuperados em um único contexto
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context_parts = []
    
    for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
        source = metadata.get('source', 'Desconhecido')
        
        # Formata o cabeçalho do documento
        header = f"[Documento {i+1}: {source}]"
        
        # Formata os metadados
        metadata_text = format_metadata(metadata)
        
        # Combina o cabeçalho, metadados e conteúdo
        doc_context = f"{header}\n{metadata_text}\n\nConteúdo:\n{doc}"
        context_parts.append(doc_context)
    
    # Junta todos os documentos com separadores claros
    context = "\n\n" + "="*50 + "\n\n".join(context_parts) + "\n\n" + "="*50 + "\n\n"
    
    return context

def query_llm(query: str, context: str, conversation_history: list) -> str:
    """Consulta o LLM com o contexto recuperado e histórico da conversa."""
    client = OpenAI()
    
    system_prompt = """Você é um assistente útil que ajuda a responder perguntas baseadas nas notas do usuário.
    Use as informações fornecidas no contexto para responder, incluindo os metadados das notas quando relevantes.
    Preste atenção especial às datas de criação e modificação, tags e outros metadados que podem ajudar a responder perguntas sobre "quando" algo aconteceu.
    Se a resposta não puder ser encontrada no contexto, diga isso claramente.
    Sempre que possível, cite os arquivos fonte das informações usando os caminhos fornecidos entre colchetes.
    Mantenha suas respostas concisas e relevantes."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Adiciona histórico da conversa
    for msg in conversation_history:
        messages.append(msg)
    
    # Adiciona contexto e pergunta atual
    messages.append({"role": "user", "content": f"Contexto:\n{context}\n\nPergunta: {query}"})
    
    response = client.chat.completions.create(
        model=COMPLETION_MODEL,
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

def print_welcome():
    """Imprime mensagem de boas-vindas."""
    print("\n=== Bem-vindo ao Chatbot do Obsidian! ===")
    print("- Digite suas perguntas para consultar suas notas")
    print("- Digite 'exit' ou 'quit' para sair")
    print("- Digite 'clear' para limpar o histórico da conversa")
    print("=========================================\n")

def main():
    # Inicializa o ChromaDB
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=EMBEDDING_MODEL
    )
    
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection("obsidian_notes", embedding_function=openai_ef)
    
    # Lista para manter o histórico da conversa
    conversation_history = []
    
    print_welcome()
    
    while True:
        try:
            # Obtém input do usuário
            query = input("\n\033[94mVocê:\033[0m ").strip()
            
            # Verifica comandos especiais
            if query.lower() in ['exit', 'quit']:
                print("\nAté logo! 👋\n")
                break
            elif query.lower() == 'clear':
                conversation_history = []
                print("\nHistórico da conversa limpo! 🧹\n")
                continue
            elif not query:
                continue
            
            # Obtém o contexto relevante
            context = get_relevant_context(query, collection)
            
            # Consulta o LLM
            response = query_llm(query, context, conversation_history)
            
            # Atualiza o histórico
            conversation_history.append({"role": "user", "content": query})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Mantém apenas as últimas 6 mensagens (3 interações) para evitar contexto muito grande
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
            
            # Imprime a resposta
            print(f"\n\033[92mAssistente:\033[0m {response}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\nAté logo! 👋\n")
            break
        except Exception as e:
            print(f"\n\033[91mOcorreu um erro: {str(e)}\033[0m")
            print("Tente novamente ou digite 'exit' para sair.\n")

if __name__ == "__main__":
    main() 