



POLICY_TEXT = (
    "Electronics items including phones and laptops may be returned within "
    "seven days of delivery if unused. Open-box items follow the same window. "
    "Contact support with your order ID for defects."
)

QUERY_KEYWORD = "electronics"
ANSWER_KEYWORD = "seven days"

TEST_CASES = [
    {
        "chunk_size": 50,
        "overlap": 10,
    },
    {
        "chunk_size": 150,
        "overlap": 20,
    }
]


def split_into_chunks(text, chunk_size, overlap):
    cnt = 0
    chunk_data = []
    while cnt < len(text):
        chunk_data.append(text[cnt : cnt+chunk_size])
        cnt = cnt + (chunk_size - overlap)
    return chunk_data

def diagnose_chunk_gap(chunks, query_keyword, answer_keyword):
    query_keyword = query_keyword.lower()
    answer_keyword = answer_keyword.lower()
    retrieved_chunk = None
    query_hit = False
    answer_hit = False

    for chunk in chunks:
        if query_keyword in chunk.lower():
            retrieved_chunk = chunk
            query_hit = True
            break

    if not query_hit:
        return {
            "query_hit": False,
            "answer_hit": False,
            "diagnosis": "weak_retrieval_miss"
        }
        
    if answer_keyword in retrieved_chunk.lower():
        answer_hit = True
        diagnosis = "ok_both_present"
    else:
        answer_exists = any(
            answer_keyword in chunk.lower() for chunk in chunks
        )
        diagnosis = (
            "weak_retrieval_split"
            if answer_exists
            else "weak_retrival_miss"
        )
    return{
        "query_hit": query_hit,
        "answer_hit": answer_hit,
        "diagnosis": diagnosis
    }

def suggest_remediation(symptom_id):
    remediations = {
        "gst_wrong_tool": (
            "tool_patch: sharpen calculate_gst description; add prompt examples"
        ),
        "missing_calculator_call": (
            "prompt_patch: must call calculate_gst for math queries"
        ),
        "tiny_chunk_miss": (
            "retrieval_tune: increase chunk_size / overlap and re-ingest"
        ),
        "refusal_on_valid_refund": (
            "prompt_patch: relax over-strict guardrails for in-domain topics"
        ),
    }

    return remediations.get(symptom_id, "unknown_symptom")


def main():
    print("=== Chunk simulation on POLICY_TEXT ===")
    for case in TEST_CASES:
        chunks = split_into_chunks(POLICY_TEXT, case["chunk_size"], case["overlap"])
        diagnosed_data = diagnose_chunk_gap(chunks, QUERY_KEYWORD, ANSWER_KEYWORD)
        print(diagnosed_data)

    print("=== Symptom → remediation hints ===")
    print(f"gst_wrong_tool: ",suggest_remediation("gst_wrong_tool"))
    print(f"missing_calculator_call: ",suggest_remediation("missing_calculator_call"))
    print(f"tiny_chunk_miss: ",suggest_remediation("tiny_chunk_miss"))
    print(f"refusal_on_valid_refund: ", suggest_remediation("refusal_on_valid_refund"))

if __name__ == "__main__":
    main()