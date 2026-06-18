from flask import Flask, render_template, request, abort, send_file, redirect
from image_cutter import crop_resize_and_compress
import io
import functools
from manga_getter import download_illust, get_image_info, web_search_work, search_novel, search_user, novel_text, novel_detail, user_works, search_illust, translate_single_title, gemini_translate_titles
from config import WINDOW_HEIGHT, WINDOW_WIDTH
from pixiv_token_manager import get_refresh_token
from math import ceil, floor
import base64

app = Flask(__name__)


def image_viewer(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        scale = request.args.get("scale")
        left = request.args.get("left")
        top = request.args.get("top")
        require_trans = request.args.get("require_trans")
        try:
            scale = float(scale)
            left = float(left)
            top = float(top)
        except (TypeError, ValueError):
            return abort(400)
        if scale <= 1:
            scale = 1
        if left < 0:
            left = 0
        if top < 0:
            top = 0
        if require_trans not in ["0", "1"]:
            require_trans = 0
        require_trans = int(require_trans)
        return func(*args, **kwargs, left=left, top=top, scale=scale, require_trans=require_trans)
    return decorated_view


def b64encode(text: str):
    return base64.b64encode(text.encode()).decode()


def b64decode(text: str):
    return base64.b64decode(text.encode()).decode()


def can_redirect(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        redirect_to = request.args.get("r")
        if not redirect_to:
            redirect_to = ""
        return func(*args, **kwargs, redirect_to=redirect_to)
    return decorated_view


@app.template_filter("ceil")
def ceil_filter(value):
    return ceil(value)


@app.template_filter("floor")
def floor_filter(value):
    return floor(value)


def translate_titles(items_full: list[dict]):
    page_size = 30
    ret = []
    for ind in range(0, len(items_full), page_size):
        if ind + page_size < len(items_full):
            items = items_full[ind: ind + page_size]
        else:
            items = items_full[ind:]
        titles = [item["title"] for item in items]
        translated_titles = gemini_translate_titles(titles)
        for i in range(len(titles)):
            items[i]["title"] = translated_titles[i]
        ret += items
    return ret


@app.route("/", methods=["get"])
def index():
    keyword = request.args.get("q")
    page_index = request.args.get("i")
    target_type = request.args.get("t")
    allow_ai = request.args.get("a")
    search_type = request.args.get("s")
    min_bookmarks = request.args.get("b")
    page_number = request.args.get("n")
    redirect_to = request.args.get("r")
    translate_title = request.args.get("tt")
    allow_r18 = request.args.get("r1")
    allow_r18g = request.args.get("r2")
    if redirect_to:
        query_string = b64decode(redirect_to)
        return redirect("/?"+query_string)
    if page_index is None:
        page_index = 0
    if min_bookmarks is None:
        min_bookmarks = 500
    if translate_title is None:
        translate_title = 0
    if allow_r18 is None:
        allow_r18 = 0
    if allow_r18g is None:
        allow_r18g = 0
    page_index = int(page_index)
    min_bookmarks = int(min_bookmarks)
    translate_title = int(translate_title)
    allow_r18 = int(allow_r18)
    allow_r18g = int(allow_r18g)
    if page_number is not None:
        page_index = int(page_number) - 1
    if page_index < 0:
        page_index = 0
    if min_bookmarks < 0:
        min_bookmarks = 0
    if target_type not in ["illust", "manga", "novel", "user", "illust_manga"]:
        target_type = "illust"
    if allow_ai not in ["1", "0"]:  # 1: 过滤AI  0: 不过滤AI
        allow_ai = "1"
    if search_type not in ["partial_match_for_tags", "exact_match_for_tags", "title_and_caption", "keyword"]:
        search_type = "partial_match_for_tags"
    if translate_title not in [0, 1]:
        translate_title = 0
    if allow_r18 not in [0, 1]:
        allow_r18 = 0
    if allow_r18g not in [0, 1]:
        allow_r18g = 0
    if not keyword:
        return render_template("index.html", keyword="", page_index=page_index, items=[],
                               target_type=target_type, allow_ai=allow_ai, search_type=search_type,
                               min_bookmarks=min_bookmarks, translate_title=translate_title,
                               allow_r18=allow_r18, allow_r18g=allow_r18g)
    if target_type in ["illust", "manga"]:
        items = web_search_work(target_type, keyword, page_index, search_type, allow_ai, allow_r18, allow_r18g)
    elif target_type == "novel":
        items = search_novel(keyword, page_index, search_type, allow_ai, min_bookmarks, allow_r18, allow_r18g)
    elif target_type == "user":
        items = search_user(keyword, page_index)
    else:
        items = search_illust(keyword, page_index, allow_ai, search_type, min_bookmarks, allow_r18, allow_r18g)
    if translate_title and target_type != "user":
        items = translate_titles(items)
    redirect_to = b64encode(request.query_string.decode())
    return render_template("index.html", keyword=keyword, page_index=page_index, items=items,
                           target_type=target_type, allow_ai=allow_ai, search_type=search_type,
                           redirect_to=redirect_to, min_bookmarks=min_bookmarks, translate_title=translate_title,
                           allow_r18=allow_r18, allow_r18g=allow_r18g)


@app.route("/watch/<int:manga_id>/<int:page_index>", methods=["get"])
@image_viewer
@can_redirect
def watch(manga_id: int, page_index: int, scale: float, top: float, left: float, require_trans: int, redirect_to: str):
    illust_info, image_urls, image_size = get_image_info(manga_id, page_index, require_trans)
    if page_index < 0:
        page_index = 0
    if page_index >= len(image_urls):
        page_index = len(image_urls) - 1
    image_width, image_height = image_size
    max_top = image_height / scale / WINDOW_HEIGHT - 1
    max_left = image_width / scale / WINDOW_WIDTH - 1
    max_scale = ceil(max(image_width / WINDOW_WIDTH, image_height / WINDOW_HEIGHT))
    if top > max_top:
        top = max_top
    if left > max_left:
        left = max_left
    if scale > max_scale:
        scale = max_scale
    return render_template("watch.html", manga_id=manga_id, page_index=page_index,
                           scale=scale, top=top, left=left, max_top=max_top, max_left=max_left,
                           max_index=len(image_urls)-1, tags=illust_info["tags"], max_scale=max_scale,
                           author=illust_info["user"], redirect_to=redirect_to, require_trans=require_trans)


@app.route("/get_image/<int:manga_id>/<int:page_index>", methods=["get"])
@image_viewer
def get_image(manga_id: int, page_index: int, scale: float, top: float, left: float, require_trans: int):
    image_bytes = download_illust(manga_id, page_index, require_trans)
    image_bytes = crop_resize_and_compress(image_bytes, scale, left, top)
    image_file = io.BytesIO(image_bytes)
    return send_file(image_file, mimetype="image/jpg")


@app.route("/read/<int:novel_id>/<int:page_index>", methods=["get"])
@can_redirect
def read(novel_id: int, page_index: int, redirect_to: str):
    require_trans = request.args.get("require_trans")
    if require_trans not in ["0", "1", "2"]:
        require_trans = 0
    require_trans = int(require_trans)
    info = novel_detail(novel_id)
    text, page_amount = novel_text(novel_id, page_index, require_trans)
    title = info["title"]
    if require_trans != 0:
        title = translate_single_title(title, require_trans)["dst"]
    return render_template("read.html", title=title, texts=text.split("\n"), tags=info["tags"], author=info["author"],
                           novel_id=novel_id, page_index=page_index, page_amount=page_amount, require_trans=require_trans,
                           redirect_to=redirect_to)


@app.route("/user/<int:uid>", methods=["get"])
@can_redirect
def user(uid: int, redirect_to: str):
    works_type = request.args.get("t")
    page_number = request.args.get("n")
    translate_title = request.args.get("tt")
    if works_type not in ["manga", "illust", "novel"]:
        works_type = "illust"
    if page_number is None:
        page_number = 1
    if translate_title not in ["0", "1"]:
        translate_title = 0
    page_number = int(page_number)
    translate_title = int(translate_title)
    if page_number < 1:
        page_number = 1
    info, works = user_works(uid, works_type, page_number - 1)
    if translate_title:
        works = translate_titles(works)
    return render_template("user.html", username=info["username"], nickname=info["nickname"], works=works,
                           page_number=page_number, uid=uid, works_type=works_type, redirect_to=redirect_to,
                           translate_title=translate_title)


@app.route("/webhook/update_token", methods=["get"])
def webhook_update_token():
    token = get_refresh_token()
    if token is not None:
        return "ok"
    return "error"


@app.errorhandler(500)
def error_500(e):
    return render_template("error.html"), 500


@app.errorhandler(400)
def error_400(e):
    return render_template("error.html"), 400


if __name__ == '__main__':
    app.run()
