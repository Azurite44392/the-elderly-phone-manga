from pixivpy3 import AppPixivAPI
from pixiv_token_manager import get_refresh_token
import requests
import brotli
import os
from config import IMAGE_CACHE_DIR, PIXIV_WEB_COOKIES, PIXIV_WEB_UID, PIXIV_SENTRY_TRACE, SEARCH_PAGE_AMOUNT_PER_PAGE, WINDOW_WIDTH, WINDOW_HEIGHT
import redis_api
import json
from image_cutter import get_image_size, resize_to_max_size_and_compress
import hashlib
from math import ceil
from baidu_translate_api import translate_image, translate_text
from translator_api import translate_texts, translate_text
import traceback


web_req_headers = {"Accept": "application/json",
                   "Accept-Encoding": "gzip, deflate, br, zstd",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                   "Baggage": "sentry-environment=production,sentry-release=a64d52acd3aace2086ab632abec7a061c10825fe,sentry-public_key=7b15ebdd9cf64efb88cfab93783df02a,sentry-trace_id=ed866abf6f144ad8977793e3c7f08fff,sentry-sample_rate=0.0001",
                   "Cookie": PIXIV_WEB_COOKIES,
                   "Priority": "u=1, i",
                   "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                   "Sec-Ch-Ua-Mobile": "?0",
                   "Sec-Ch-Ua-Platform": '"Windows"',
                   "Sec-Fetch-Dest": "empty",
                   "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Site": "same-origin",
                   "Sentry-Trace": PIXIV_SENTRY_TRACE,
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                   "X-User-Id": PIXIV_WEB_UID}


def construct_headers(kwargs: dict):
    headers = web_req_headers.copy()
    for k, v in kwargs.items():
        headers[k] = v
    return headers


def get_md5(sth: str):
    return hashlib.md5(sth.encode("utf-8")).hexdigest()


def download_image(url: str):
    req_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                   "Referer": "https://www.pixiv.net/"}
    rsp = requests.get(url, headers=req_headers)
    if rsp.status_code == 200:
        return rsp.content
    return None


def calculate_max_scale(image_width: int, image_height: int):
    max_scale = ceil(max(image_width / WINDOW_WIDTH, image_height / WINDOW_HEIGHT))
    return max_scale


def get_illust_urls(illust_id: int):
    db_session = redis_api.get_session()
    data = db_session.get(f"pixiv_illust_data_{illust_id}")
    if data is not None:
        data = json.loads(data)
        image_urls = data["image_urls"]
        info = data["info"]
    else:
        api_instance = AppPixivAPI()
        api_instance.auth(refresh_token=get_refresh_token())
        rsp = api_instance.illust_detail(illust_id)
        if "illust" not in rsp:
            db_session.close()
            return None
        info = rsp["illust"]
        if "meta_single_page" in info and info["meta_single_page"] != {}:
            image_urls = [info["meta_single_page"]["original_image_url"]]
        elif "meta_pages" in info:
            image_urls = [i["image_urls"]["original"] for i in info["meta_pages"]]
        else:
            db_session.close()
            return None
        db_session.set(f"pixiv_illust_data_{illust_id}", json.dumps({"image_urls": image_urls, "info": info}))
    db_session.expire(f"pixiv_illust_data_{illust_id}", 24*3600)  # 刷新ttl
    db_session.close()
    return image_urls, info


def get_image_info(illust_id: int, page_index: int, require_trans: int):
    image_urls, illust_info = get_illust_urls(illust_id)
    image_size = get_image_size(download_illust(illust_id, page_index, require_trans))
    return illust_info, image_urls, image_size


def _download_illust(illust_id: int, page_index: int):
    if os.path.isfile(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}.jpg')):
        with open(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}.jpg'), 'rb') as f:
            image_bytes = f.read()
        return image_bytes
    image_urls, _ = get_illust_urls(illust_id)
    if image_urls is None:
        return None
    if page_index < 0:
        page_index = 0
    if page_index > len(image_urls) - 1:
        page_index = len(image_urls) - 1
    image_bytes = download_image(image_urls[page_index])
    with open(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}.jpg'), "wb") as f:
        f.write(image_bytes)
    return image_bytes


def download_illust(illust_id: int, page_index: int, require_trans: int):
    if require_trans == 0:
        return _download_illust(illust_id, page_index)
    if os.path.isfile(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}_translated.jpg')):
        with open(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}_translated.jpg'), 'rb') as f:
            image_bytes = f.read()
        return image_bytes
    origin_image = _download_illust(illust_id, page_index)
    origin_image = resize_to_max_size_and_compress(origin_image, 4096, 95)
    result, errcode, data = translate_image("auto", "zh", origin_image, "jpg")
    if not result:
        print(f"Failed to translate image. error code: {errcode}")
        return None
    translated_image = data["dst_image"]
    with open(os.path.join(IMAGE_CACHE_DIR, f'{illust_id}_{page_index}_translated.jpg'), 'wb') as f:
        f.write(translated_image)
    return translated_image


# deprecated
def search_artwork(offset_s: int, artwork_type: str, keyword: str, page_size: int = 10, allow_ai: str = "1", search_type: str = "partial_match_for_tags"):
    offset = offset_s
    results = []
    while len(results) < page_size:
        rsp = search_illust(keyword, offset, allow_ai, search_type)
        for i in rsp:
            if i["type"] == artwork_type:
                results.append(i)
            offset += 1
    return results, offset


def search_illust(keyword: str, page_index: int, allow_ai: str = "0", search_type: str = "partial_match_for_tags", min_bookmarks: int = 0, allow_r18: int = 0, allow_r18g: int = 0):
    cache_key = get_md5(f"q={keyword}&i={page_index}&a={allow_ai}&t={search_type}&a=illust_manga")
    db_session = redis_api.get_session()
    data = db_session.get(f"pixiv_search_cache_{cache_key}")
    if data is None:
        api_instance = AppPixivAPI()
        api_instance.auth(refresh_token=get_refresh_token())
        all_results = []
        for i in range(SEARCH_PAGE_AMOUNT_PER_PAGE):
            search_param = {"filter": "for_ios", "offset": str(30 * (page_index * SEARCH_PAGE_AMOUNT_PER_PAGE + i)),
                            "search_target": search_type, "sort": "date_desc",
                            "word": keyword, "search_ai_type": int(allow_ai)}
            rsp = api_instance.search_illust(**search_param)
            if "illusts" not in rsp:
                continue
            result = [{"title": item["title"], "author": item["user"]["name"], "is_ai": item["illust_ai_type"] == 2,
                       "id": item["id"], "type": item["type"], "bookmarks": item['total_bookmarks'],
                       "pages": item["page_count"], "max_scale": calculate_max_scale(item["width"], item["height"]),
                       "restrict_lvl": item["x_restrict"]} for item in rsp["illusts"]]
            all_results += result
        db_session.set(f"pixiv_search_cache_{cache_key}", json.dumps(all_results))
    else:
        all_results = json.loads(data)
    db_session.expire(f"pixiv_search_cache_{cache_key}", 30 * 60)  # 刷新ttl
    db_session.close()
    all_results = [item for item in all_results
                   if item['bookmarks'] >= min_bookmarks and (allow_r18 or item["restrict_lvl"] != 1) and (allow_r18g or item["restrict_lvl"] != 2)
                   ]
    all_results.sort(key=lambda x: x['bookmarks'], reverse=True)
    return all_results


def web_search_work(artwork_type: str, keyword: str, page_index: int, search_type: str = "partial_match_for_tags", allow_ai: str = "1", allow_r18: int = 0, allow_r18g: int = 0):
    if artwork_type == "manga":
        url_artwork_type = args_artwork_type = "manga"
    else:
        url_artwork_type = "illustrations"
        args_artwork_type = "illust_and_ugoira"
    if search_type == "partial_match_for_tags":
        search_type = "s_tag"
    elif search_type == "exact_match_for_tags":
        search_type = "s_tag_full"
    else:
        search_type = "s_tc"
    req_headers = construct_headers({})
    req_data = {"word": keyword, "order": "date_d", "mode": "all", "p": str(page_index+1), "csw": "0",
                "s_mode": search_type, "type": args_artwork_type, "lang": "zh",
                "version": "a64d52acd3aace2086ab632abec7a061c10825fe"}
    if allow_ai == "1":
        req_data["ai_type"] = "1"
    rsp = requests.get(f"https://www.pixiv.net/ajax/search/{url_artwork_type}/{keyword}",
                       headers=req_headers, params=req_data)
    rsp = json.loads(rsp.text)
    if rsp["error"]:
        print(rsp)
        return None
    data = rsp["body"][artwork_type]["data"]
    results = [{"title": item["title"], "author": item["userName"], "is_ai": item["aiType"] == 2,
                "id": item["id"], "max_scale": calculate_max_scale(item["width"], item["height"]),
                "restrict_lvl": item["xRestrict"]} for item in data]
    results = [item for item in results
               if (allow_r18 or item["restrict_lvl"] != 1) and (allow_r18g or item["restrict_lvl"] != 2)
               ]
    return results


def search_user(keyword: str, page_index: int):
    api_instance = AppPixivAPI()
    api_instance.auth(refresh_token=get_refresh_token())
    search_param = {"word": keyword, "offset": 30 * page_index}
    rsp = api_instance.search_user(**search_param)
    if "user_previews" not in rsp:
        return []
    results = [{"nickname": item["user"]["name"], "username": item["user"]["account"],
                "id": item["user"]["id"]} for item in rsp["user_previews"]]
    return results


def search_novel(keyword: str, page_index: int, search_type: str = "partial_match_for_tags", allow_ai: str = "1", min_bookmarks: int = 0, allow_r18: int = 0, allow_r18g: int = 0):
    cache_key = get_md5(f"q={keyword}&i={page_index}&a={allow_ai}&t={search_type}&a=novel")
    db_session = redis_api.get_session()
    data = db_session.get(f"pixiv_search_cache_{cache_key}")
    if data is None:
        api_instance = AppPixivAPI()
        api_instance.auth(refresh_token=get_refresh_token())
        all_results = []
        for i in range(SEARCH_PAGE_AMOUNT_PER_PAGE):
            search_param = {"word": keyword, "search_target": search_type, "search_ai_type": int(allow_ai),  # 是否显示AI作品参数似乎无效
                            "offset": 30 * (page_index * SEARCH_PAGE_AMOUNT_PER_PAGE + i)}
            rsp = api_instance.search_novel(**search_param)
            if "novels" not in rsp:
                continue
            results = [{"title": item["title"], "author": item["user"]["name"],
                        "is_ai": item["novel_ai_type"] == 2, "id": item["id"],
                        "bookmarks": item['total_bookmarks'],
                        "restrict_lvl": item["x_restrict"]} for item in rsp["novels"]]
            all_results += results
        db_session.set(f"pixiv_search_cache_{cache_key}", json.dumps(all_results))
    else:
        all_results = json.loads(data)
    db_session.expire(f"pixiv_search_cache_{cache_key}", 60 * 30)
    db_session.close()
    all_results = [item for item in all_results
                   if item["bookmarks"] >= min_bookmarks and (allow_r18 or item["restrict_lvl"] != 1) and (allow_r18g or item["restrict_lvl"] != 2)
                   ]
    all_results.sort(key=lambda x: x["bookmarks"], reverse=True)
    return all_results


def user_works(uid: int, work_type: str, page_index: int):
    api_instance = AppPixivAPI()
    api_instance.auth(refresh_token=get_refresh_token())
    if work_type != "novel":
        param = {"user_id": uid, "type": work_type, "offset": 30 * page_index}
        rsp = api_instance.user_illusts(**param)
        works = [{"type": item["type"], "title": item["title"], "is_ai": item["illust_ai_type"] == 2,
                  "id": item["id"], "restrict_lvl": item["x_restrict"]} for item in rsp["illusts"]]
        user = {"username": rsp["user"]["account"], "nickname": rsp["user"]["name"], "id": rsp["user"]["id"]}
        return user, works
    param = {"user_id": uid, "offset": 30 * page_index}
    rsp = api_instance.user_novels(**param)
    works = [{"type": "novel", "title": item["title"], "is_ai": item["novel_ai_type"] == 2,
              "id": item["id"], "restrict_lvl": item["x_restrict"]} for item in rsp["novels"]]
    user = {"username": rsp["user"]["account"], "nickname": rsp["user"]["name"], "id": rsp["user"]["id"]}
    return user, works


def _novel_text(work_id: int, page_index: int):
    db_session = redis_api.get_session()
    cache_key = f"pixiv_novel_text_cache_{work_id}_v2"
    data = db_session.get(cache_key)
    if data is None:
        api_instance = AppPixivAPI()
        api_instance.auth(refresh_token=get_refresh_token())
        rsp = api_instance.novel_text(work_id)
        # 分页
        paged_texts = []
        text = ""
        for i in rsp["novel_text"].split("\n"):
            text += i + "\n"
            if len(text) > 500:
                paged_texts.append(text)
                text = ""
        if text:
            paged_texts.append(text)
        db_session.setex(cache_key, 3600*24, json.dumps(paged_texts))
    else:
        paged_texts = json.loads(data)
    db_session.close()
    return paged_texts[page_index], len(paged_texts)


def novel_text(work_id: int, page_index: int, require_trans: int):
    if require_trans == 0:
        return _novel_text(work_id, page_index)
    cache_key = f"pixiv_novel_translated_cache_{work_id}_{page_index}_{require_trans}_v2"
    db_session = redis_api.get_session()
    data = db_session.get(cache_key)
    if data is None:
        origin_text, page_amount = _novel_text(work_id, page_index)
        if require_trans == 1:
            result, errcode, translated = translate_text("auto", "zh", origin_text)
            if not result:
                print(f"Failed to translate text. error code:{errcode}")
                db_session.close()
                return "错误:无法翻译文本", 1
            page_info = {"text": translated["dst"], "page_amount": page_amount}
        elif require_trans == 2:
            try:
                result = translate_text(origin_text)
            except:
                print("Gemini failed to translate text.", traceback.format_exc())
                db_session.close()
                return "错误:无法翻译文本", 1
            page_info = {"text": result["translated_text"], "page_amount": page_amount}
        else:
            db_session.close()
            return "错误:未知的翻译接口", 1
        db_session.setex(cache_key, 3600*24, json.dumps(page_info))
    else:
        page_info = json.loads(data)
    db_session.close()
    return page_info["text"], page_info["page_amount"]


def novel_detail(work_id: int):
    api_instance = AppPixivAPI()
    api_instance.auth(refresh_token=get_refresh_token())
    rsp = api_instance.novel_detail(work_id)
    return {"title": rsp["novel"]["title"], "tags": rsp["novel"]["tags"], "author": rsp["novel"]["user"]}


def translate_single_title(title: str, require_trans: int):
    cache_key = f"pixiv_title_translation_cache_{get_md5(title)}_{require_trans}"
    db_session = redis_api.get_session()
    data = db_session.get(cache_key)
    if data is None:
        if require_trans == 1:
            result, errcode, info = translate_text("auto", "zh", title)
            if not result:
                db_session.close()
                print(f"Failed to translate text. error code:{errcode}")
                return {"src_lang": "zh", "dst": "标题翻译失败"}
        elif require_trans == 2:
            try:
                result = translate_text(title)
            except:
                db_session.close()
                print(f"Gemini failed to translate text.", traceback.format_exc())
                return {"src_lang": "zh", "dst": "标题翻译失败"}
            info = {"src_lang": result.get("source_language"), "dst": result["translated_text"]}
        else:
            db_session.close()
            return {"src_lang": None, "dst": "未知翻译接口"}
        db_session.setex(cache_key, 86400*2, json.dumps(info))
    else:
        info = json.loads(data)
    db_session.close()
    return info


def gemini_translate_titles(titles: list[str]):
    db_session = redis_api.get_session()
    require_trans = []
    translation_map = {}
    ret = []
    for title in titles:
        title_md5 = get_md5(title)
        cache_key = f"pixiv_titles_translation_cache_{title_md5}"
        data = db_session.get(cache_key)
        if data is None:
            if title not in require_trans:
                require_trans.append(title)
        else:
            data = json.loads(data)
            translation_map[title_md5] = data["dst"]
    if len(require_trans) > 0:
        try:
            results = translate_texts(require_trans)
        except:
            results = [{"source_language": "", "translated_text": "标题翻译失败"} for _ in range(len(require_trans))]
    else:
        results = []
    if len(results) != len(require_trans):
        for i in require_trans:
            translation_map[get_md5(i)] = "标题翻译失败"
    else:
        for i in range(len(require_trans)):
            title_md5 = get_md5(require_trans[i])
            translation_map[title_md5] = results[i]["translated_text"]
            if results[i]["translated_text"] != "标题翻译失败":
                cache_key = f"pixiv_titles_translation_cache_{title_md5}"
                db_session.setex(cache_key, 2*86400,
                                 json.dumps({"src_lang": results[i].get("source_language"),
                                             "dst": results[i]["translated_text"]}))
    for t in titles:
        ret.append(translation_map[get_md5(t)])
    db_session.close()
    return ret


if __name__ == "__main__":
    print(search_illust("test", 0))
