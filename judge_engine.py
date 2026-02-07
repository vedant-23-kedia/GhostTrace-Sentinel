import sys
import ollama
import chromadb
# This line must match your file name and function name!
from file_scanner import get_project_code_content 

def run_sentinel_audit():
    print("🛡️ GhostTrace: Sentinel - Commencing Logic Audit...")
    
    # Use the NEW function name you created
    project_path = r"C:\Users\samru\Desktop\GhostTrace"
    code_data = get_project_code_content(project_path)
    
    # Convert the dictionary into one big string for the AI
    current_code = ""
    for filename, content in code_data.items():
        current_code += f"\n--- FILE: {filename} ---\n{content}\n"

    # 1. Connect to Memory (ChromaDB)
    client = chromadb.PersistentClient(path="./ghosttrace_db")
    collection = client.get_collection(name="business_rules")
    rules_data = collection.query(query_texts=["ui requirements"], n_results=3)
    rules = "\n".join(rules_data['documents'][0])

    # 2. Ask the AI Judge
    prompt = f"RULES:\n{rules}\n\nCODE:\n{current_code}\n\nTask: If code breaks rules, say 'STATUS: FAIL'. If not, 'STATUS: PASS'."

    try:
        response = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        return f"STATUS: FAIL - Error: {e}"

if __name__ == "__main__":
    result = run_sentinel_audit()
    print(f"\nAUDIT REPORT:\n{result}")
    
    # EXIT CODES: 0 = Success, 1 = Blocked
    sys.exit(0 if "STATUS: PASS" in result else 1)