import google.generativeai as genai
import typing_extensions as typing
import json
from config import GEMINI_API_KEY


class Translation(typing.TypedDict):
    source_language: str
    translated_text: str


def gemini_translate_text(text: str, to_lang: str = "Simplified Chinese"):
    text = text.replace("[newpage]", "").replace("[chapter:", "").replace("{", "").replace("}", "").replace("[", "").replace("]", "")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
    prompt = f"Translate the following text to {to_lang}:\n\n{text}"
    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=Translation
        )
    )
    return json.loads(result.text)


def gemini_translate_texts(texts: list[str], to_lang: str = "Simplified Chinese"):
    for i in range(len(texts)):
        texts[i] = texts[i].replace("\n", " ")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
    prompt = "Translate each line of text below into {} individually. Note that the language of each line of text may be different.\n\n{}".format(to_lang, '\n\n'.join(texts))
    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=list[Translation]
        )
    )
    return json.loads(result.text)


if __name__ == "__main__":
    print(gemini_translate_text("こんにちは", "English"))
