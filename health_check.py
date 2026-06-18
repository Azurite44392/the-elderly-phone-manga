import requests
import brotli
import sys

try:
    rsp = requests.get(
        "http://127.0.0.1:5025/",
        timeout=3,
        headers={
            "User-Agent": "Internal Health Check",
        }
    )
    if "老人机漫画站" in rsp.text:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    sys.exit(1)
