import os
import json
from pathlib import Path
from openai import OpenAI

# Uses OPENAI_API_KEY from .env (loaded by settings)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# The only model we use — no fallback, no preview, no mini
MODEL = "gpt-4.1"

# ---------- vector store helpers ----------

def _create_vector_store(name: str = "feinlab-run"):
    try:
        return client.vector_stores.create(name=name)
    except Exception:
        return client.beta.vector_stores.create(name=name)

def _upload_pdf_to_vector_store(vs_id: str, pdf_path: str):
    try:
        with open(pdf_path, "rb") as fh:
            return client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vs_id,
                files=[fh],
            )
    except Exception:
        with open(pdf_path, "rb") as fh:
            return client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vs_id,
                files=[fh],
            )

# ---------- output extraction ----------

def _extract_output_text(resp) -> str:
    out = getattr(resp, "output", None)
    if isinstance(out, list):
        parts = []
        for msg in out:
            content = getattr(msg, "content", None)
            if isinstance(content, list):
                for c in content:
                    txt = getattr(c, "text", None)
                    if isinstance(txt, str) and txt.strip():
                        parts.append(txt)
            mtxt = getattr(msg, "text", None)
            if isinstance(mtxt, str) and mtxt.strip():
                parts.append(mtxt)
        if parts:
            return "\n".join(parts)

    txt = getattr(resp, "output_text", None)
    if isinstance(txt, str) and txt.strip():
        return txt

    return str(resp)

def _parse_text_to_json(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except:
        pass
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
    except:
        pass
    return {"error": "non_json_output", "raw": text[:2000]}

# ---------- core run ----------

def _to_json_or_retry(tool_call, _sys_prompt_note: str):
    user_msg = {"role": "user", "content": "Use only the uploaded PDF via File Search."}

    # Try strict JSON
    try:
        resp = tool_call(
            model=MODEL,
            response_format={"type": "json_object"},
            temperature=0,
            max_output_tokens=200000,
            user_msg=user_msg,
        )
        data = _parse_text_to_json(_extract_output_text(resp))
        if "error" not in data:
            return data
    except TypeError:
        pass
    except Exception:
        pass

    # Retry without response_format
    resp = tool_call(
        model=MODEL,
        temperature=0,
        max_output_tokens=200000,
        user_msg=user_msg,
    )
    return _parse_text_to_json(_extract_output_text(resp))

# ---------- response builders ----------

def _responses_with_file_search(sys_prompt: str, vector_store_id: str, **kw):
    try:
        args = dict(
            model=kw.get("model", MODEL),
            temperature=kw.get("temperature", 0),
            max_output_tokens=kw.get("max_output_tokens"),
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
            input=[{"role": "system", "content": sys_prompt}, kw["user_msg"]],
        )
        if "response_format" in kw:
            args["response_format"] = kw["response_format"]
        return client.responses.create(**args)
    except TypeError:
        args = dict(
            model=kw.get("model", MODEL),
            temperature=kw.get("temperature", 0),
            tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
            input=[{"role": "system", "content": sys_prompt}, kw["user_msg"]],
        )
        return client.responses.create(**args)

def _responses_with_file_id(sys_prompt: str, file_id: str, **kw):
    try:
        args = dict(
            model=kw.get("model", MODEL),
            temperature=kw.get("temperature", 0),
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": [{"type": "input_file", "file_id": file_id}]},
            ],
        )
        if "response_format" in kw:
            args["response_format"] = kw["response_format"]
        return client.responses.create(**args)
    except:
        args = dict(
            model=kw.get("model", MODEL),
            temperature=kw.get("temperature", 0),
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"File ID: {file_id}"},
            ],
        )
        return client.responses.create(**args)

# ---------- public API ----------

def analyze_pdf_with_file_search(pdf_path: str, prompt: str) -> dict:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(pdf_path)

    vs = _create_vector_store()
    _upload_pdf_to_vector_store(vs.id, str(p))

    def tool_call(**kw):
        return _responses_with_file_search(prompt, vs.id, **kw)

    return _to_json_or_retry(tool_call, prompt)

def analyze_pdf_direct(pdf_path: str, prompt: str) -> dict:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(pdf_path)

    with open(p, "rb") as fh:
        file_obj = client.files.create(file=fh, purpose="assistants")

    def tool_call(**kw):
        return _responses_with_file_id(prompt, file_obj.id, **kw)

    return _to_json_or_retry(tool_call, prompt)
