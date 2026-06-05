from build_chain import build_chain

chain = build_chain()

def is_response_valid(response: str) -> tuple[bool, list[str]]:
    """
    Validate whether the response generated follows the defined criteria or not.

    Success Criteria:
    1. Response must be a string.
    2. Response must not be empty.
    3. Response must not be more than 500 words.
    """

    errors = []
    if not isinstance(response, str):
        errors.append("Response must be a string")
        return False, errors
    
    if len(response) == 0:
        errors.append("Response must not be empty")
        return False, errors

    if len(response.split()) > 500:
        errors.append("Response must not be more than 500 words")
        return False, errors
    
    return True, errors

TEST_CASES = [
    {
        "topic":"LangChain Expression Language",
        "analogy_domain":"school assembly line"
    },
    {
        "topic":"Prompt Templates",
        "analogy_domain":"wedding invitation card"
    },
    {
        "topic":"Output Parsers",
        "analogy_domain":"Food delivery packaging"
    }
]

for case in TEST_CASES:
    response = chain.invoke(case)
    print(f"Input Dictionary:{case}")
    print(f"Generated Response:\n{response}\n")
    isValid, validation_errors = is_response_valid(response)
    if isValid:
        print("Response is valid")
    else:
        print("Response is invalid. Errors:", validation_errors)