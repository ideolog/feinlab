import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_from_pdf(pdf_path: str, prompt: str, model: str = "gpt-4.1-mini"):
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(pdf_path)

    with open(pdf_file, "rb") as f:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f.read()},
            ],
        )

    return response.output_text
