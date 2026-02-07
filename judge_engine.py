import ollama
import chromadb
import json

# 1. Connect to the Memory (Member 2's part)
client = chromadb.PersistentClient(path="./ghosttrace_db")
collection = client.get_collection(name="business_rules")

def run_judge_audit(extracted_json):
    print("⚖️ GhostTrace: Sentinel - Commencing Logic Audit...")

    # 2. Query Memory for relevant rules
    # We search the database for rules related to 'Payment' and 'UI'
    results = collection.query(
        query_texts=["payment checkout UI components and validation"],
        n_results=5
    )
    retrieved_rules = "\n".join(results['documents'][0])

    # 3. The Triple-Sync Prompt
    prompt = f"""
    Act as a Senior QA Auditor. Compare the DETECTED UI against the BUSINESS RULES.
    
    BUSINESS RULES FROM MEMORY:
    {retrieved_rules}
    
    DETECTED UI FROM SKETCH:
    {extracted_json}
    
    TASK:
    Identify any MISSING components or RULE VIOLATIONS.
    If everything is correct, say 'STATUS: PASS'.
    If there is a mistake, say 'STATUS: FAIL' and list the reasons.
    """

    try:
        # 4. Use Llama 3.2 (Text model) to judge
        response = ollama.chat(
            model='llama3.2:3b', # Pull this if you haven't: ollama pull llama3.2:3b
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Judge Error: {str(e)}"

# For testing, we use your previous Vision output
sample_json = """
[ { "type": "button", "label": "Payment Checkout" },
  { "type": "input field", "label": "Cardholder Name" } ]
"""

if __name__ == "__main__":
    audit_report = run_judge_audit(sample_json)
    print("\n--- FINAL AUDIT REPORT ---")
    print(audit_report)