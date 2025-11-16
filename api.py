from http.client import HTTPException
from fastapi import FastAPI
from models import ClaimRequest, ClaimResponse, ClaimListResponse
from processor import process_claim, test_model
from storage import save_claim_result, load_claim_result, list_all_results, save_test_results

app = FastAPI()

@app.post("/claims", response_model=ClaimResponse)
def submit_claim(req: ClaimRequest):
    claim_id = req.claim_id

    processed_claim = process_claim(claim_id)

    result = ClaimResponse(
        claim_id=claim_id,
        decision=processed_claim["decision"],
        confidence=processed_claim["confidence"],
        explanation=processed_claim["explanation"],
    )

    save_claim_result(result)
    return result

@app.get("/claims/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: int):
    stored = load_claim_result(claim_id)
    if stored is None:
        raise HTTPException()
    return stored

@app.get("/claims", response_model=ClaimListResponse)
def list_claims():
    return ClaimListResponse(claims=list_all_results())

@app.post("/claims/test-model", response_model=ClaimListResponse)
def submit_all_claims():
    all_results = []

    accuracy, processed_claims = test_model()

    for i, processed_claim in enumerate(processed_claims):
        result = ClaimResponse(
            claim_id=i+1,
            decision=processed_claim["decision"],
            confidence=processed_claim["confidence"],
            explanation=processed_claim["explanation"],
        )
        save_claim_result(result)
        all_results.append(result)

    response = ClaimListResponse(claims=all_results)
    save_test_results(accuracy, response)
    return response