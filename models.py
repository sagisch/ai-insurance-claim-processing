from pydantic import BaseModel
from typing import List


class ClaimRequest(BaseModel):
    claim_id: int

class ClaimResponse(BaseModel):
    claim_id: int
    decision: str
    confidence: str
    explanation: str

class ClaimListResponse(BaseModel):
    claims: List[ClaimResponse]
