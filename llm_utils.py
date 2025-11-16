import base64
import json
import os
from pathlib import Path
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def build_claim(claim_dir: str):
    """
    Create a dictionary for the claim data
    :param claim_dir: where the individual claim is stored
    :return: a dictionary containing the claim data
    """

    claim_path = Path(claim_dir)

    description = ""
    supporting_docs = []
    supporting_images = []

    for file_path in sorted(claim_path.iterdir()):
        file_name = file_path.name

        if file_name == "answer.json":  # If there is no ground truth, we can't use this claim
            continue

        elif file_name == "description.txt":
            description = file_path.read_text(encoding="utf-8")

        elif file_path.suffix in {".md", ".txt"}:
            supporting_docs.append(file_path.read_text(encoding="utf-8"))

        elif file_path.suffix in {".webp", ".jpg", ".jpeg", ".png"}:
            supporting_images.append(encode_image(str(file_path)))

        else:
            raise Exception(f"The file type is not supported: {file_name}")

    return {
        "description": description,
        "supporting_docs": supporting_docs,
        "supporting_images": supporting_images,
    }

def build_prompt(claim_dir: str, policy_dir: str):
    """
    Build the input for the OpenAI LLM
    :param claim_dir: where the individual claim is stored
    :param policy_dir: where the policy prompy is stored
    :return: the input for the OpenAI LLM
    """

    claim = build_claim(claim_dir)
    description = claim["description"]
    supporting_docs = claim["supporting_docs"]
    supporting_images = claim["supporting_images"]

    policy = Path(policy_dir).read_text()

    contents = [{
        "role": "user",
        "content": [{"type": "input_text", "text": f"## Policy:\n{policy}"}]
    }, {
        "role": "user",
        "content": [{"type": "input_text", "text": f"## Claim Description:\n{description}"}]
    }]

    for i, doc in enumerate(supporting_docs, 1):
        contents.append({
            "role": "user",
            "content": [{"type": "input_text", "text": f"## Supporting Document {i}:\n{doc}"}]
        })

    for img_b64 in supporting_images:
        contents.append({
            "role": "user",
            "content": [{"type": "input_image", "image_url": f"data:image/jpeg;base64,{img_b64}"}]
        })

    return contents

def analyze_claim(claim_dir: str, policy_path: str):
    """
    Give the claim data to the LLM (GPT 5 mini)
    :param claim_dir: where the individual claim is stored
    :param policy_path: where the policy prompy is stored
    :return: the LLM response
    """

    model_input = build_prompt(claim_dir, policy_path)

    response = client.responses.create(
        model="gpt-5-mini",
        input=model_input,
    )

    output = response.output_text

    try:
        result = json.loads(output)
    except json.decoder.JSONDecodeError:
        raise ValueError(f"Model did not return a valid json: {output}")

    return {
        "decision": str(result["decision"]),
        "confidence": str(result["confidence"]),
        "explanation": str(result["explanation"]),
    }
