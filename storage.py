import json
from pathlib import Path
from models import ClaimResponse, ClaimListResponse


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TESTS_DIR = Path("tests")
TESTS_DIR.mkdir(parents=True, exist_ok=True)

def save_claim_result(result: ClaimResponse):
    file = RESULTS_DIR / f"claim_{result.claim_id}.json"
    file.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"Saved claim_{result.claim_id} to {file}")

def load_claim_result(claim_id: int):
    file = RESULTS_DIR / f"claim_{claim_id}.json"
    if not file.exists():
        return None
    return json.loads(file.read_text())

def list_all_results():
    results = []
    for file in RESULTS_DIR.glob("claim_*.json"):
        results.append(json.loads(file.read_text()))
    return results

def save_test_results(accuracy: float, all_results: ClaimListResponse):
    file = next_available_filename()
    data = {
        "accuracy": accuracy,
        "claims": [c.model_dump() for c in all_results.claims],
    }
    file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved test results to {file}")

def next_available_filename(base="test", ext: str = ".json", tests_dir: Path = TESTS_DIR):
    """
    Return the next available file name, to avoid overwriting tests
    :param base: the base name of the file
    :param ext: the extension of the file
    :param tests_dir: the directory where the tests are stored
    :return: the next available file name
    """
    first = tests_dir / f"{base}{ext}"
    if not first.exists():
        return first

    i = 2
    while True:
        candidate = tests_dir / f"{base}_{i}{ext}"
        if not candidate.exists():
            return candidate
        i += 1