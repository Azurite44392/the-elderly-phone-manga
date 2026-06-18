import requests
import brotli
import json
import time
import redis_api
from config import NETWORK_PROXIES, PIXIV_INIT_TOKEN

# Latest app version can be found using GET /v1/application-info/android
USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


# credit: https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
def _get_refreshed_token(old_refresh_token: str):
    rsp = requests.post(
        AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "include_policy": "true",
            "refresh_token": old_refresh_token,
        },
        headers={"User-Agent": USER_AGENT},
        proxies=NETWORK_PROXIES
    )
    rsp = json.loads(rsp.text)
    if "access_token" in rsp and "refresh_token" in rsp:
        return rsp["access_token"], rsp["refresh_token"], rsp.get("expires_in", 0)
    return None, None, None


def update_token():
    db_session = redis_api.get_session()
    token = db_session.get("pixiv_auth")
    if token is None:
        db_session.close()
        raise RuntimeError("Old token not found")
    token = json.loads(token)
    access_token, refresh_token, expires_in = _get_refreshed_token(token["refresh_token"])
    if access_token is None:
        db_session.close()
        raise RuntimeError("Could not refresh token")
    data = {"access_token": access_token, "refresh_token": refresh_token, "expires_in": expires_in,
            "create_at": time.time()}
    db_session.set("pixiv_auth", json.dumps(data))
    db_session.close()
    return True


def get_refresh_token():
    db_session = redis_api.get_session()
    token = db_session.get("pixiv_auth")
    if token is None:
        return None
    token = json.loads(token)
    if time.time() - token["create_at"] > token["expires_in"]:
        update_token()
        token = db_session.get("pixiv_auth")
        token = json.loads(token)
    db_session.close()
    return token["access_token"], token["refresh_token"]


def set_token(access_token: str, refresh_token: str, expires_in: int):
    data = {"access_token": access_token, "refresh_token": refresh_token, "expires_in": expires_in,
            "create_at": time.time()}
    db_session = redis_api.get_session()
    db_session.set("pixiv_auth", json.dumps(data))
    db_session.close()
    return True


def _init():
    token = get_refresh_token()
    if token is None:
        set_token(*PIXIV_INIT_TOKEN)
        update_token()


_init()
if __name__ == "__main__":
    pass
