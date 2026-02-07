import sys
import ollama
import chromadb
from file_scanner import get_code_snapshot  # <--- Member 3's Reader

def run_real_audit():
    print("🛡️ Sentinel is scanning your project files...")
    
    # 1. Get the actual code from the folder
    current_code = get_code_snapshot(".")
    
    # 2. Get the rules from Memory (Member 2's Database)
    client = chromadb.PersistentClient(path="./ghosttrace_db")
    collection = client.get_collection(name="business_rules")
    rules = collection.query(query_texts=["payment checkout rules"], n_results=3)
    business_context = "\n".join(rules['documents'][0])

    # 3. The Triple-Sync Prompt
    prompt = f"""
    AUDIT TASK: Compare the Code below against the Business Rules.
    
    RULES:
    {business_context}
    
    DEVELOPER CODE:
    {current_code}
    
    If the code violates any rules (e.g. wrong button label, missing fields), 
    output 'STATUS: FAIL' and list reasons.
    If it matches perfectly, output 'STATUS: PASS'.
    """

    try:
        # 4. Use the Judge (Llama 3.2)
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"STATUS: FAIL - AI Error: {str(e)}"

if __name__ == "__main__":
    final_report = run_real_audit()
    print("\n--- SENTINEL REPORT ---")
    print(final_report)
    
    # THE GATEKEEPER LOGIC
    if "STATUS: PASS" in final_report:
        sys.exit(0) # Allow Push
    else:
        sys.exit(1) # Block Push