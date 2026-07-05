import requests
from config import CF_ACCOUNT_ID, CF_API_TOKEN, CF_MODEL


def cloudflare_translate_text(text: str, to_lang: str = "Simplified Chinese"):
    text = text.replace("[newpage]", "") \
               .replace("[chapter:", "") \
               .replace("{", "") \
               .replace("}", "") \
               .replace("[", "") \
               .replace("]", "")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"Translate the following text to {to_lang}:\n\n{text}"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "type": "object",
                "properties": {
                    "source_language": {"type": "string"},
                    "translated_text": {"type": "string"}
                },
                "required": ["source_language", "translated_text"]
            }
        },
        "max_tokens": 30000
    }

    rsp = requests.post(url, headers=headers, json=payload)
    data = rsp.json()
    return data["result"]["response"]


def cloudflare_translate_texts(texts: list[str], to_lang: str = "Simplified Chinese"):
    texts = [t.replace("\n", " ") for t in texts]
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    input_text = "\n\n".join(texts)
    schema = {
        "type": "object",
        "properties": {
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source_language": {"type": "string"},
                        "translated_text": {"type": "string"}
                    },
                    "required": ["source_language", "translated_text"]
                }
            }
        },
        "required": ["translations"]
    }
    prompt = f"""
Translate each line into {to_lang} independently.

Rules:
- Do not merge lines
- Keep order
- Return JSON matching schema exactly

Input:
{input_text}
"""
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": schema
        },
        "max_tokens": 30000
    }

    rsp = requests.post(url, headers=headers, json=payload)
    data = rsp.json()
    return data["result"]["response"]["translations"]
