import sqlite3
import os
import shutil
from pathlib import Path
import glob

def get_notes_db_path():
    """Encontra o caminho do banco de dados do Notes."""
    notes_dir = Path.home() / "Library" / "Group Containers" / "group.com.apple.notes"
    db_pattern = str(notes_dir / "NoteStore.sqlite")
    db_files = glob.glob(db_pattern)
    
    if not db_files:
        return None
        
    # Cria uma cópia temporária do banco de dados para evitar problemas de permissão
    temp_db = Path("temp_notes.db")
    try:
        shutil.copy2(db_files[0], temp_db)
        return str(temp_db)
    except PermissionError:
        print("Erro de permissão ao acessar o banco de dados do Notes.")
        print("Por favor, dê permissão de acesso total ao disco para o Terminal nas Preferências do Sistema > Privacidade e Segurança > Acesso Total ao Disco")
        return None
    except Exception as e:
        print(f"Erro ao copiar banco de dados: {e}")
        return None

def extract_apple_notes():
    """Extrai todas as notas do Apple Notes."""
    db_path = get_notes_db_path()
    if not db_path:
        print("Banco de dados do Apple Notes não encontrado ou sem permissão de acesso.")
        return []
    
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query principal para extrair notas
        query = """
        SELECT 
            note.ZTITLE,
            note.ZDISPLAYTEXT,
            note.ZSTANDARDIZEDCONTENT,
            note.ZSNIPPET
        FROM 
            ZICCLOUDSYNCINGOBJECT note 
        WHERE 
            note.ZTITLE IS NOT NULL
            AND note.ZMARKEDFORDELETION = 0
            AND (
                note.ZDISPLAYTEXT IS NOT NULL 
                OR note.ZSTANDARDIZEDCONTENT IS NOT NULL 
                OR note.ZSNIPPET IS NOT NULL
            )
        ORDER BY 
            note.ZMODIFICATIONDATE DESC
        """
        
        cursor.execute(query)
        notes = cursor.fetchall()
        print(f"\nNotas encontradas: {len(notes)}")
        
        # Formata as notas
        formatted_notes = []
        for title, display_text, std_content, snippet in notes:
            if title:
                # Usa o melhor conteúdo disponível na ordem: display_text > std_content > snippet
                content = display_text or std_content or snippet
                if content:
                    note_text = f"# {title}\n\n{content}"
                    formatted_notes.append({
                        "content": note_text,
                        "source": f"apple_notes/{title.replace('/', '_')}.txt"
                    })
        
        print(f"Notas válidas encontradas: {len(formatted_notes)}")
        
        # Remove o arquivo temporário
        if db_path.startswith("temp_"):
            try:
                os.remove(db_path)
            except:
                pass
                
        return formatted_notes
        
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados do Apple Notes: {e}")
        return []
    except Exception as e:
        print(f"Erro ao processar notas do Apple Notes: {e}")
        return []
    finally:
        try:
            conn.close()
        except:
            pass 