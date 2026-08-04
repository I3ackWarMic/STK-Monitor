import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGETS = {
    "pledge1_login": "https://pledge1.bangkok.go.th/sec_Login/",
    "pledge1_root": "https://pledge1.bangkok.go.th/",
    "pawnshop_webboard": "http://pawnshop.bangkok.go.th/webboard/",
    "pawnshop_index": "http://pawnshop.bangkok.go.th/indexnew.html",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

def get_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def check_site(name, url, timeout=15):
    s = get_session()
    try:
        resp = s.get(url, headers=HEADERS, timeout=timeout, verify=False, allow_redirects=True)
        return {"name": name, "url": url, "status_code": resp.status_code,
                "up": resp.status_code < 400, "error": None}
    except requests.exceptions.RequestException as e:
        return {"name": name, "url": url, "status_code": None,
                "up": False, "error": repr(e)}

def check_all():
    return [check_site(name, url) for name, url in TARGETS.items()]

if __name__ == "__main__":
    for r in check_all():
        print(r)
