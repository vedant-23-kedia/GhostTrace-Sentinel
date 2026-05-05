import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTEXT_PATH = os.path.join(BASE_DIR, "current_context.json")
REPORT_PATH = os.path.join(BASE_DIR, "latest_report.json")
BAD_CODE_PATH = os.path.join(BASE_DIR, "bad_code.html")


def load_context():
    if os.path.exists(CONTEXT_PATH):
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def read_code_file():
    if os.path.exists(BAD_CODE_PATH):
        with open(BAD_CODE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def write_report(status, reason, developer="GhostTrace Team", failed_rules=None):
    report = {
        "status": status,
        "reason": reason,
        "developer": developer,
        "failed_rules": failed_rules or [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("STATUS:", status)
    print("REASON:", reason)

    if failed_rules:
        print("\nFAILED GOVERNANCE RULES:")
        for i, rule in enumerate(failed_rules, start=1):
            print(f"{i}. {rule}")


def run_mock_audit():
    context = load_context()

    developer = context.get("developer", "GhostTrace Team")
    requirement = context.get("requirement", "")
    code = read_code_file()

    if not requirement.strip():
        write_report(
            "FAIL",
            "No requirement found. Please sync requirement first from dashboard.",
            developer,
            ["Missing Requirement Context"]
        )
        return "FAIL"

    if not code.strip():
        write_report(
            "FAIL",
            "No code file found. Please create or update bad_code.html first.",
            developer,
            ["Missing Code File"]
        )
        return "FAIL"

    requirement_lower = requirement.lower()
    code_lower = code.lower()

    failed_rules = []

    if "pay now" in requirement_lower and "pay now" not in code_lower:
        failed_rules.append(
            "Pay Now Button Rule violated: Requirement expects a button labeled 'Pay Now', but code does not contain 'Pay Now'."
        )

    if "pay now" in requirement_lower and "submit" in code_lower:
        failed_rules.append(
            "Button Label Mismatch: Requirement expects 'Pay Now', but code uses 'Submit'."
        )

    if "blue" in requirement_lower and "blue" not in code_lower:
        failed_rules.append(
            "Blue Button Rule violated: Requirement expects a blue button, but code does not contain blue styling."
        )

    if "blue" in requirement_lower and "red" in code_lower:
        failed_rules.append(
            "Color Governance Rule violated: Requirement expects blue button, but code contains red styling."
        )

    if "cardholder name" in requirement_lower and "cardholder name" not in code_lower:
        failed_rules.append(
            "Cardholder Name Field Rule violated: Requirement expects Cardholder Name field, but code does not contain it."
        )

    if "card number" in requirement_lower and "card number" not in code_lower:
        failed_rules.append(
            "Card Number Field Rule violated: Requirement expects Card Number field, but code does not contain it."
        )

    if "expiry date" in requirement_lower and "expiry date" not in code_lower:
        failed_rules.append(
            "Expiry Date Field Rule violated: Requirement expects Expiry Date field, but code does not contain it."
        )

    if "cvv" in requirement_lower and "cvv" not in code_lower:
        failed_rules.append(
            "CVV Field Rule violated: Requirement expects CVV field, but code does not contain it."
        )

    if "delete all user data" in code_lower or "drop database" in code_lower:
        failed_rules.append(
            "Safety Rule violated: Code contains destructive action such as DELETE ALL USER DATA or database deletion."
        )

    if failed_rules:
        reason = "Commit rejected because the following governance rules are violated:\n\n"
        for i, rule in enumerate(failed_rules, start=1):
            reason += f"{i}. {rule}\n"

        write_report("FAIL", reason, developer, failed_rules)
        return "FAIL"

    write_report(
        "PASS",
        "Commit verified. Code satisfies the current governance rules.",
        developer,
        []
    )
    return "PASS"


if __name__ == "__main__":
    result = run_mock_audit()
    sys.exit(0 if result == "PASS" else 1)