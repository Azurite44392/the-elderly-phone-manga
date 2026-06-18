import os

# gunicorn 配置
port = 5025
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "15"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "2000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "200"))
real_ip_header = os.getenv("GUNICORN_REAL_IP_HEADER", "")  # 存放客户端 IP 的请求头，如果不使用反代则留空

# 应用配置
WINDOW_WIDTH = int(os.getenv("EPM_WINDOW_WIDTH", "240"))
WINDOW_HEIGHT = int(os.getenv("EPM_WINDOW_HEIGHT", "240"))

NETWORK_PROXIES = {}  # deprecated

IMAGE_CACHE_DIR = "./cache/"  # 斜杠结尾
SEARCH_PAGE_AMOUNT_PER_PAGE = int(os.getenv("EPM_SEARCH_PAGE_AMOUNT_PER_PAGE", "5"))

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "")

# Pixiv 配置
PIXIV_INIT_TOKEN = [
    os.getenv("PIXIV_ACCESS_TOKEN"),
    os.getenv("PIXIV_REFRESH_TOKEN"),
    int(os.getenv("PIXIV_EXPIRE_IN", "3600"))
]
PIXIV_WEB_COOKIES = os.getenv("PIXIV_WEB_COOKIES", "")
PIXIV_WEB_UID = os.getenv("PIXIV_WEB_UID", "")
PIXIV_SENTRY_TRACE = os.getenv("PIXIV_SENTRY_TRACE", "")

# 百度翻译配置
BAIDU_TRANSLATE_APPID = os.getenv("BAIDU_TRANSLATE_APPID", "")
BAIDU_TRANSLATE_SECRET = os.getenv("BAIDU_TRANSLATE_SECRET", "")

# Gemini 翻译配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
