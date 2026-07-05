from config import AI_TRANSLATOR
import gemini_translate_api
import cf_translate_api


def translate_text(*args):
    if AI_TRANSLATOR == "gemini":
        return gemini_translate_api.gemini_translate_text(*args)
    elif AI_TRANSLATOR == "cloudflare":
        return cf_translate_api.cloudflare_translate_text(*args)
    else:
        raise ValueError("Unknown AI translator: {}".format(AI_TRANSLATOR))


def translate_texts(*args):
    if AI_TRANSLATOR == "gemini":
        return gemini_translate_api.gemini_translate_texts(*args)
    elif AI_TRANSLATOR == "cloudflare":
        return cf_translate_api.cloudflare_translate_texts(*args)
    else:
        raise ValueError("Unknown AI translator: {}".format(AI_TRANSLATOR))
