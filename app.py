import os
import time
import json
import requests
import urllib3
from flask import Flask
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

TARGETS = {
    "pledge1_login": "https://pledge1.bangkok.go.th/sec_Login/",
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
    start = time.time()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout,
                             verify=False, allow_redirects=True)
        elapsed_ms = round((time.time() - start) * 1000)
        return {
            "name": name,
            "url": url,
            "status_code": resp.status_code,
            "up": resp.status_code < 400,
            "error": None,
            "response_ms": elapsed_ms,
        }
    except requests.exceptions.RequestException as e:
        elapsed_ms = round((time.time() - start) * 1000)
        return {
            "name": name,
            "url": url,
            "status_code": None,
            "up": False,
            "error": repr(e),
            "response_ms": elapsed_ms,
        }


@app.route("/")
def index():
    results = [check_site(name, url) for name, url in TARGETS.items()]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    online_count = sum(1 for r in results if r["up"])
    total_count = len(results)

    chart_labels = json.dumps([r["name"] for r in results])
    chart_response_times = json.dumps([r["response_ms"] for r in results])
    chart_colors = json.dumps(["#3ddc84" if r["up"] else "#ff5c5c" for r in results])

    rows = ""
    for r in results:
        if r["up"]:
            badge = '<span class="badge online">🟢 ONLINE</span>'
        else:
            badge = '<span class="badge offline">🔴 OFFLINE</span>'
        code_display = r["status_code"] if r["status_code"] else "-"
        error_display = r["error"] if r["error"] else "-"
        rows += f"""
        <tr>
            <td class="name">{r['name']}</td>
            <td class="url"><a href="{r['url']}" target="_blank">{r['url']}</a></td>
            <td>{badge}</td>
            <td class="code">{code_display}</td>
            <td>{r['response_ms']} ms</td>
            <td class="error">{error_display}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="60">
        <title>STK Monitor</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: 'Segoe UI', Tahoma, sans-serif;
                background: #0f1117;
                color: #e6e6e6;
                padding: 40px 20px;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ font-size: 28px; margin-bottom: 4px; }}
            .subtitle {{ color: #8b8f9a; font-size: 14px; margin-bottom: 24px; }}
            .summary {{ display: flex; gap: 16px; margin-bottom: 24px; }}
            .card {{
                background: #1a1d27; border: 1px solid #2a2e3a;
                border-radius: 10px; padding: 16px 20px; flex: 1;
            }}
            .card .num {{ font-size: 26px; font-weight: bold; }}
            .card .label {{ font-size: 13px; color: #8b8f9a; margin-top: 4px; }}
            .card.up .num {{ color: #3ddc84; }}
            .card.down .num {{ color: #ff5c5c; }}
            .charts {{
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 16px;
                margin-bottom: 24px;
            }}
            .chart-box {{
                background: #1a1d27;
                border: 1px solid #2a2e3a;
                border-radius: 10px;
                padding: 20px;
            }}
            .chart-box h3 {{ font-size: 14px; color: #8b8f9a; margin-bottom: 12px; }}
            table {{
                width: 100%; border-collapse: collapse;
                background: #1a1d27; border-radius: 10px; overflow: hidden;
            }}
            th {{
                background: #21252f; text-align: left; padding: 12px 16px;
                font-size: 13px; color: #8b8f9a; text-transform: uppercase;
            }}
            td {{ padding: 14px 16px; border-top: 1px solid #2a2e3a; font-size: 14px; vertical-align: top; }}
            .name {{ font-weight: 600; }}
            .url a {{ color: #6ea8fe; text-decoration: none; word-break: break-all; }}
            .url a:hover {{ text-decoration: underline; }}
            .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
            .badge.online {{ background: rgba(61,220,132,0.15); color: #3ddc84; }}
            .badge.offline {{ background: rgba(255,92,92,0.15); color: #ff5c5c; }}
            .code {{ color: #8b8f9a; }}
            .error {{ color: #ff9d9d; font-size: 12px; max-width: 240px; word-break: break-word; }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #565a66; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛰️ STK Monitor</h1>
            <div class="subtitle">อัปเดตล่าสุด: {now} · รีเฟรชอัตโนมัติทุก 60 วินาที</div>

            <div class="summary">
                <div class="card up"><div class="num">{online_count}</div><div class="label">ONLINE</div></div>
                <div class="card down"><div class="num">{total_count - online_count}</div><div class="label">OFFLINE</div></div>
                <div class="card"><div class="num">{total_count}</div><div class="label">TOTAL SITES</div></div>
            </div>

            <div class="charts">
                <div class="chart-box">
                    <h3>สัดส่วนสถานะ</h3>
                    <canvas id="statusChart"></canvas>
                </div>
                <div class="chart-box">
                    <h3>Response Time (ms)</h3>
                    <canvas id="speedChart"></canvas>
                </div>
            </div>

            <table>
                <tr>
                    <th>Name</th><th>URL</th><th>Status</th><th>Code</th><th>Response</th><th>Error</th>
                </tr>
                {rows}
            </table>

            <div class="footer">STK-Monitor · Powered by Flask on Render</div>
        </div>

        <script>
            new Chart(document.getElementById('statusChart'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Online', 'Offline'],
                    datasets: [{{
                        data: [{online_count}, {total_count - online_count}],
                        backgroundColor: ['#3ddc84', '#ff5c5c'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    plugins: {{ legend: {{ labels: {{ color: '#e6e6e6' }} }} }}
                }}
            }});

            new Chart(document.getElementById('speedChart'), {{
                type: 'bar',
                data: {{
                    labels: {chart_labels},
                    datasets: [{{
                        label: 'Response time (ms)',
                        data: {chart_response_times},
                        backgroundColor: {chart_colors}
                    }}]
                }},
                options: {{
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#8b8f9a' }}, grid: {{ color: '#2a2e3a' }} }},
                        y: {{ ticks: {{ color: '#8b8f9a' }}, grid: {{ color: '#2a2e3a' }} }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
