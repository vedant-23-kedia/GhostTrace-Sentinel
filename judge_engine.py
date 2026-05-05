import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTEXT_PATH = os.path.join(BASE_DIR, "current_context.json")
REPORT_PATH = os.path.join(BASE_DIR, "latest_report.json")
BAD_CODE_PATH = os.path.join(BASE_DIR, "bad_code.html")


def write_report(status, reason, failed_rules=None):
    report = {
        "status": status,
        "reason": reason,
        "developer": "GhostTrace Team",
        "failed_rules": failed_rules or [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("STATUS:", status)
    print("REASON:", reason)

    if failed_rules:
        print("\nFAILED GOVERNANCE RULES:")
        for index, rule in enumerate(failed_rules, start=1):
            print(f"{index}. {rule}")


def read_bad_code():
    if not os.path.exists(BAD_CODE_PATH):
        return ""

    with open(BAD_CODE_PATH, "r", encoding="utf-8-sig", errors="replace") as file:
        return file.read()


def run_audit():
    print("READING FILE FROM:", BAD_CODE_PATH)

    code = read_bad_code()
    code_lower = code.lower()

    print("\nCODE FOUND:")
    print("--------------------------------")
    print(code[:500].encode("ascii", errors="ignore").decode())
    print("--------------------------------\n")

    failed_rules = []

    if not code.strip():
        failed_rules.append("bad_code.html is empty or not found.")

    if "submit" in code_lower:
        failed_rules.append("Button Label Rule violated: Code uses Submit, but expected Pay Now.")

    if "red" in code_lower:
        failed_rules.append("Color Rule violated: Code uses red styling, but expected blue.")

    if "delete all user data" in code_lower:
        failed_rules.append("Safety Rule violated: Code contains DELETE ALL USER DATA.")

    if "pay now" not in code_lower:
        failed_rules.append("Pay Now Rule violated: Code does not contain Pay Now button.")

    if "blue" not in code_lower:
        failed_rules.append("Blue Button Rule violated: Code does not contain blue styling.")

    if "cardholder name" not in code_lower:
        failed_rules.append("Missing Field Rule: Cardholder Name field is missing.")

    if "card number" not in code_lower:
        failed_rules.append("Missing Field Rule: Card Number field is missing.")

    if "expiry date" not in code_lower:
        failed_rules.append("Missing Field Rule: Expiry Date field is missing.")

    if "cvv" not in code_lower:
        failed_rules.append("Missing Field Rule: CVV field is missing.")

    if failed_rules:
        reason = "Commit rejected because the code violates governance rules:\n\n"
        for index, rule in enumerate(failed_rules, start=1):
            reason += f"{index}. {rule}\n"

        write_report("FAIL", reason, failed_rules)
        return "FAIL"

    write_report(
        "PASS",
        "Commit verified. Code satisfies all secure checkout governance rules.",
        []
    )
    return "PASS"


if __name__ == "__main__":
    result = run_audit()
    sys.exit(0 if result == "PASS" else 1)