import json
from pathlib import Path
from llm_utils import analyze_claim


def process_claim(claim_id: int, claims_dir="data", policy_path="prompts/policy.txt"):
    print(f"Processing claim {claim_id}")
    claim_dir = f"{claims_dir}/claim {claim_id}"

    return analyze_claim(claim_dir, policy_path)


def test_model(claims_dir="data", policy_path="prompts/policy.txt"):
    """
    Test the pipeline using all the given claims - analyze each claim and return accuracy.
    :param claims_dir: where the individual claim is stored
    :param policy_path: where the policy prompy is stored
    :return: accuracy and the LLM response to the claims
    """
    correct = 0
    total = 0
    test_data_path = Path(claims_dir)
    processed_claims = []

    print("Processing claims...")
    for claim_dir in sorted(test_data_path.iterdir()):
        if not claim_dir.is_dir():
            continue

        answer_path = claim_dir / "answer.json"
        if not answer_path.exists():
            raise Exception(f"{claim_dir.name} is not labeled and should not be in test data")

        label = json.loads(answer_path.read_text())["decision"]
        prediction = analyze_claim(str(claim_dir), policy_path)
        processed_claims.append(prediction)

        if prediction["decision"] == label:
            correct += 1

        total += 1

    accuracy = correct / total if total else 0
    print(f"Accuracy: {accuracy:.4%}")
    return accuracy, processed_claims

