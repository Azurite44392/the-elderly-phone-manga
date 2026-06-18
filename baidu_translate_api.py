import requests
import brotli
import json
import hashlib
import random
from config import BAIDU_TRANSLATE_APPID, BAIDU_TRANSLATE_SECRET
import base64


LANG_KEYS = {
    "auto": "自动检测",
    "zh": "中文",
    "en": "英语",
    "yue": "粤语",
    "wyw": "文言文",
    "jp": "日语",
    "kor": "韩语",
    "fra": "法语",
    "spa": "西班牙语",
    "th": "泰语",
    "ara": "阿拉伯语",
    "ru": "俄语",
    "pt": "葡萄牙语",
    "de": "德语",
    "it": "意大利语",
    "el": "希腊语",
    "nl": "荷兰语",
    "pl": "波兰语",
    "bul": "保加利亚语",
    "est": "爱沙尼亚语",
    "dan": "丹麦语",
    "fin": "芬兰语",
    "cs": "捷克语",
    "rom": "罗马尼亚语",
    "slo": "斯洛文尼亚语",
    "swe": "瑞典语",
    "hu": "匈牙利语",
    "cht": "繁体中文",
    "vie": "越南语"}


def gen_salt():
    return str(random.randint(100000, 999999))


def calculate_md5(src: bytes):
    md5 = hashlib.md5()
    md5.update(src)
    return md5.hexdigest()


def base64_decode(a: str):
    return base64.b64decode(a.encode())


def translate_text(src_lang: str, to_lang: str, text: str):
    salt = gen_salt()
    sign = calculate_md5(f"{BAIDU_TRANSLATE_APPID}{text}{salt}{BAIDU_TRANSLATE_SECRET}".encode())
    req_payload = {"q": text,
                   "from": src_lang,
                   "to": to_lang,
                   "appid": BAIDU_TRANSLATE_APPID,
                   "salt": salt,
                   "sign": sign}
    rsp = requests.post("https://fanyi-api.baidu.com/api/trans/vip/translate",
                        data=req_payload,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    rsp = json.loads(rsp.text)
    if "error_code" in rsp:
        return False, rsp["error_code"], None
    dsts = [i["dst"] for i in rsp["trans_result"]]
    return True, 0, {"src_lang": rsp["from"], "dst": "\n".join(dsts)}


def translate_image(src_lang: str, to_lang: str, image_file: bytes, file_suffix: str):
    salt = gen_salt()
    req_files = {"image": (f"image.{file_suffix}", image_file, "multipart/form-data")}
    req_payload = {"from": src_lang,
                   "to": to_lang,
                   "appid": BAIDU_TRANSLATE_APPID,
                   "salt": salt,
                   "cuid": "APICUID",
                   "mac": "mac",
                   "version": 3,
                   "paste": 1}
    sign = calculate_md5(f"{BAIDU_TRANSLATE_APPID}{calculate_md5(image_file)}{salt}{req_payload['cuid']}{req_payload['mac']}{BAIDU_TRANSLATE_SECRET}".encode())
    req_payload["sign"] = sign
    rsp = requests.post("https://fanyi-api.baidu.com/api/trans/sdk/picture",
                        data=req_payload,
                        files=req_files)
    rsp = json.loads(rsp.text)
    if rsp["error_code"] != "0":
        return False, rsp["error_code"], None
    return True, 0, {"src_lang": rsp["data"]["from"], "dst_image": base64_decode(rsp["data"]["pasteImg"])}


if __name__ == "__main__":
    pass

