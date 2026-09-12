# webapp/app.py
# Flask app nhỏ, cố ý có lỗi, dùng để ZAP quét DAST qua HTTP thật.
# Chạy: pip install -r requirements.txt && python app.py
# Mặc định chạy ở http://localhost:5000

from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return "<h1>Vuln Test Webapp</h1><p>Endpoints: /login, /search, /file</p>"


@app.route("/login", methods=["GET", "POST"])
def login():
    # Lỗi: SQL Injection - nối chuỗi trực tiếp vào query (CWE-89)
    username = request.values.get("username", "")
    password = request.values.get("password", "")
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor = conn.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return "Login OK"
    return "Login failed"


@app.route("/search")
def search():
    # Lỗi: Reflected XSS - trả input người dùng thẳng vào HTML không escape (CWE-79)
    q = request.args.get("q", "")
    template = f"<p>Kết quả tìm kiếm cho: {q}</p>"
    return render_template_string(template)


@app.route("/file")
def get_file():
    # Lỗi: Path Traversal - không kiểm tra tên file (CWE-22)
    filename = request.args.get("name", "readme.txt")
    path = os.path.join(os.path.dirname(__file__), "files", filename)
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return str(e), 400


if __name__ == "__main__":
    init_db()
    os.makedirs(os.path.join(os.path.dirname(__file__), "files"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "files", "readme.txt"), "w", encoding="utf-8") as f:
        f.write("Đây là file mẫu, không chứa gì nhạy cảm.")
    app.run(host="0.0.0.0", port=5000, debug=True)
