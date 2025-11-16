# LLM-based Insurance Claim Processing Pipeline

### Overview 

This pipeline takes an insurance claim containing a claim description (generally explaining the claim) 
and supporting documents (e.g. medical statements and invoices), and classifies the claim with APPROVE/DENY/UNCERTAIN.
The classification is done with OpenAI GPT 5 mini.

### Approach

To understand what kind of challenges there might be with classifying the claims, I first created a summary of all ground-truth
(`answer.json`) files. I saw that common pitfalls could be accepting claims without valid signatures, missing dates, etc.
The code is in `eda.ipynb` and the summary is in `claim_summary.csv`.

Since I had only 25 labeled claims, there was no chance of training a model from scratch using this little amount of data.
Due to the complexity of the data (multiple formats, multilingual) and the challenge in detecting unauthentic claims, using an LLM
seemed the right approach. First, my idea was to use the LLM for extracting data about the claim, and then using hard rules
to determine its status, which could give more flexibility and control. However, the number of edge cases is big and this approach
seemed too complex. Therefore, I relied solely on the LLM logic for making the predictions. 

For each claim, I passed to the LLM the claim description and the supporting documents (including images). Additionally, I
provided the LLM with the given insurance policy that I adjusted (e.g., removed irrelevant information), which I also augmented 
with examples of which claim cases should be denied. The prompt is available in `prompts/policy.txt`. Finally, I asked 
the LLM to give a confidence score between 0 and 1 and explain the reasoning in one sentence.

The accuracy using this pipeline was 72%. The predictions are available in `tests/test.json`.  

### Possible Extensions

1. Using the confidence score provided by the LLM for thresholding. 
For example, approving only classifications with confidence level of 0.9 or above. 
2. Extracting metadata from documents to assess their authenticity (checking when the document was created, etc).
3. Analyzing misclassifications in the available test data to further tune prompt.
4. Using a different LLM, or using an ensemble of LLMs which will be aggregated for a final prediction.
5. Extracting features and using hard rules for claims (e.g., if no date appears on the provided document then deny).

### Setup

Make sure you have:

- Python 3.11+
- uv package manager. Install if needed: https://docs.astral.sh/uv/getting-started/installation/

Create a virtual environment and activate it (windows):
```aiignore
uv venv
.\.venv\Scripts\Activate.ps1
```

Install project dependencies
```aiignore
uv sync
```

Add your OpenAI API key as an environment variable:
```aiignore
setx OPENAI_API_KEY "your_api_key_here"
```

Start the server:
```bash
    python main.py
```

Alternatively (for auto-reloading):
```bash
    uvicorn app.main:app --reload
```

Open your browser: 
```aiignore
http://localhost:8000/docs/
```

### API Endpoints

| Method | Path               | Description                                          |
|--------|--------------------|------------------------------------------------------|
| POST   | /claims            | Submit and analyze a claim (with ClaimRequest)       |
| POST   | /claims/test-model | Submit and analyze all claims (computes performance) |
| GET    | /claims/{id}       | Get claim with id                                    |
| GET    | /claims            | List all claims                                      |
