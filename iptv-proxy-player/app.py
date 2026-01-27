from flask import Flask, Response, request
import requests

app = Flask(__name__)

HEADERS = {
    "Referer": "https://v5on.site/",
    "User-Agent": "Mozilla/5.0"
}

@app.route("/stream")
def stream():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    r = requests.get(url, headers=HEADERS, stream=True)
    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("Content-Type")
    )

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
