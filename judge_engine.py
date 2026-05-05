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


def write_report(status, reason, developer="GhostTrace Team"):
    report = {
        "status": status,
        "reason": reason,
        "developer": developer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("STATUS:", status)
    print("REASON:", reason)


def run_mock_audit():
    context = load_context()

    developer = context.get("developer", "GhostTrace Team")
    requirement = context.get("requirement", "")
    code = read_code_file()

    if not requirement.strip():
        write_report(
            "FAIL",
            "No requirement found. Please sync requirement first from dashboard.",
            developer
        )
        return "FAIL"

    requirement_lower = requirement.lower()
    code_lower = code.lower()

    # FAIL condition 1: destructive unsafe code
    if "delete all user data" in code_lower or "drop database" in code_lower:
        write_report(
            "FAIL",
            "Commit rejected because destructive or unsafe code was detected.",
            developer
        )
        return "FAIL"

    # FAIL condition 2: wrong checkout button
    if "pay now" in requirement_lower and "submit" in code_lower and "pay now" not in code_lower:
        write_report(
            "FAIL",
            "Commit rejected because requirement expects a Pay Now button, but code uses Submit instead.",
            developer
        )
        return "FAIL"

    # FAIL condition 3: red button while blue button required
    if "blue" in requirement_lower and "red" in code_lower and "blue" not in code_lower:
        write_report(
            "FAIL",
            "Commit rejected because requirement expects a blue button, but code appears to use red styling.",
            developer
        )
        return "FAIL"

    # PASS condition
    if "payment" in requirement_lower or "pay now" in requirement_lower or "checkout" in requirement_lower:
        write_report(
            "PASS",
            "Commit verified. Requirement found and code passed the current governance checks.",
            developer
        )
        return "PASS"

    # Default FAIL
    write_report(
        "FAIL",
        "Commit rejected. Requirement does not match the expected payment/checkout governance policy.",
        developer
    )
    return "FAIL"


if __name__ == "__main__":
    result = run_mock_audit()
    sys.exit(0 if result == "PASS" else 1)