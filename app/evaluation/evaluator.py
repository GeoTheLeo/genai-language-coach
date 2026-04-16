def evaluate_output(output: dict):
    """
    Basic evaluation metrics for LLM output quality.
    """

    score = {
        "valid_json": isinstance(output, dict),
        "has_phrases": "phrases" in output,
        "num_phrases": len(output.get("phrases", [])),
    }

    return score