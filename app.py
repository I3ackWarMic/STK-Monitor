import os
import requests
import urllib3
from flask import Flask
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

TARGETS = {
    "pledge1_login": "https://pledge1.bangkok.go.th/",
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

def check_site(name, url, timeout=15):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout,
                             verify=False, allow_redirects=True)
        return {
            "name": name,
            "url": url,
            "status_code": resp.status_code,
            "up": resp.status_code < 400,
            "error": None,
        }
    except requests.exceptions.RequestException as e:
        return {
            "name": name,
            "url": url,
            "status_code": None,
            "up": False,
            "error": repr(e),
        }

@app.route("/")
def index():
    results = [check_site(name, url) for name, url in TARGETS.items()]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for r in results:
        color = "green" if r["up"] else "red"
        status_text = "ONLINE" if r["up"] else "OFFLINE"
        rows += f"""
        <tr>
            <td>{r['name']}</td>
            <td>{r['url']}</td>
            <td style="color:{color}; font-weight:bold;">{status_text}</td>
            <td>{r['status_code']}</td>
            <td>{r['error'] or '-'}</td>
        </tr>
        """

    html = f"""
    <html>
    <head><meta charset="utf-8"><title>STK Monitor</title></head>
    <body style="font-family: sans-serif;">
        <h2>STK Monitor - Last check: {now}</h2>
        <table border="1" cellpadding="8" style="border-collapse: collapse;">
            <tr>
                <th>Name</th><th>URL</th><th>Status</th><th>Code</th><th>Error</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
