import csv
import json
from pathlib import Path
from typing import Any, Dict, List

RESULTS_PATH = Path("results.csv")

REFUSAL_PHRASES=[
    "i don't have",
    "cannot provide",
    "not available",
    "i cannot help"
]

MOCK_RUNS={
    "refund_policy": {
        "tools_used":["search_course_policy"],
        "final_response": "As per refund_policy, you get 100% refund within 7 days."
    },
    "pause_policy": {
        "tools_used": ["search_course_policy"],
        "final_response": "You may pause enrollment once per cohort.",
    },
    "private_phone_refusal":{
        "tools_used": [],
        "final_response": "I cannot provide personal contact information."
    }
}

def load_cases(path: str = "evaluation_cases.json") -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def normalize(text: str) -> str:
    return text.lower().strip()

def contains_refusal(text: str) -> bool:
    text = normalize(text)
    return any(phrase in text for phrase in REFUSAL_PHRASES)

def get_retrieved_doc_ids(trace: Dict[str, Any]) -> List[str]:
    ids = []
    for doc_data in trace.get("retrievals", []):
        for doc in doc_data.get("documents", []):
            ids.append(doc["doc_id"])
    return sorted(set(ids))

def evaluate_case(
        case: Dict[str, Any],
        tools_used: List[str],
        final_response: str) -> Dict[str, Any]:
    expected = case["expected"]
    final_lower = normalize(final_response)
    failures = []

    # 1. Required tools
    for tool in expected.get("must_use_tools",[]):
        if tool not in tools_used:
            failures.append(
                {
                    "type":"TOOL_MISSING",
                    "message":f"Expected tool is missing: {tool}"
                }
            )

    # 2. Required Answer Content
    for phrase in expected.get("must_contain", []):
        if normalize(phrase) not in final_lower:
            failures.append(
                {
                    "type": "CONTENT_MISSING",
                    "message": f"Expected phrase missing: {phrase}"
                }
            )

    # 3. Refusal Behaviour
    expected_refusal = expected.get("should_refuse", False)
    actual_refusal = contains_refusal(final_lower)

    if expected_refusal and not actual_refusal:
        failures.append(
            {
                "type": "REFUSAL_MISSING",
                "message": "Expected refusal but agent answered."
            }
        )
    
    if not expected_refusal and actual_refusal:
            failures.append(
                {
                    "type": "OVER_REFUSAL",
                    "message": "Agent refused even though it should answer.",
                }
            )
    status = "PASS" if not failures else "FAIL"
    score = max(0.0, 1.0 - 0.25 * len(failures))

    return{
        "case_id": case["id"],
        "status": status,
        "score": score,
        "failures": failures,
        "tools_used": tools_used,
        "final_response": final_response
    }




def write_results(rows):
    fieldnames = [
        "case_id",
        "status",
        "score",
        "failures",
        "tools_used",
        "final_response"
    ]

    with open(RESULTS_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "status": row["status"],
                    "score": row["score"],
                    "failures": row["failures"],
                    "tools_used": row["tools_used"],
                    "final_response": row["final_response"]
                }
            )

def main():
    cases = load_cases()
    results = []
    for case in cases:
        mock = MOCK_RUNS[case["id"]]
        scored = evaluate_case(case, mock["tools_used"], mock["final_response"])
        results.append(scored)
        print(f"{scored['case_id']}: {scored['status']} (score={scored['score']})")
    write_results(results)
    passed = sum(1 for r in results if r["status"].lower() == "pass")
    print(f"\nPassed: {passed} / {len(results)}")

if __name__ == "__main__":
    main()