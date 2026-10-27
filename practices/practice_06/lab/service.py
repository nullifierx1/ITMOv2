"""Deliberately vulnerable local shop. All identities and data are synthetic."""

import argparse
import json
import sqlite3
import threading
import uuid
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from sandbox import Sandbox


class Shop:
    def __init__(self):
        self.sandbox = Sandbox()
        self.lock = threading.RLock()
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE profiles(id INTEGER PRIMARY KEY, name TEXT, email TEXT, address TEXT);
            INSERT INTO profiles VALUES
                (1, 'TEST_ALICE', 'alice@example.invalid', 'TEST_ADDRESS_A'),
                (2, 'TEST_BOB', 'bob@example.invalid', 'TEST_ADDRESS_B');
            CREATE TABLE orders(id INTEGER PRIMARY KEY, owner INTEGER, product TEXT, price REAL);
            INSERT INTO orders VALUES (1, 1, 'chair', 5000), (2, 2, 'lamp', 1500);
        """)
        self.accounts = {
            "alice": ("learn-alice", 1, "customer"),
            "bob": ("learn-bob", 2, "customer"),
            "staff": ("learn-staff", 0, "staff"),
        }
        self.sessions = {}
        self.products = {"chair": 5000, "lamp": 1500}
        self.reviews = []
        self.logs = []
        # Reverse mapping from id to username for file ownership checks
        self.usernames = {1: "alice", 2: "bob"}

    def rows(self, query, params=()):
        return [dict(row) for row in self.db.execute(query, params)]

    def _get_session(self, headers):
        return self.sessions.get(headers.get("X-Token"))

    def _is_staff(self, headers):
        s = self._get_session(headers)
        return bool(s and s.get("role") == "staff")

    def _append_log(self, method, target):
        # Store minimal transport info; avoid bodies and secret headers
        self.logs.append({"method": method, "target": target})
        # Limit accumulated logs (S11)
        if len(self.logs) > 100:
            self.logs.pop(0)

    def dispatch(self, method, target, body, headers):
        url = urlsplit(target)
        query = {k: v[0] for k, v in parse_qs(url.query, keep_blank_values=True).items()}
        # Minimal logging without secrets (S07)
        self._append_log(method, target)
        if method == "GET" and url.path == "/health":
            return 200, {"status": "ok"}
        if method == "GET" and url.path == "/products":
            return 200, self.products
        if method == "POST" and url.path == "/login":
            account = self.accounts.get(body.get("username"))
            if not account or body.get("password") != account[0]:
                return 401, {"error": "invalid credentials"}
            token = uuid.uuid4().hex
            self.sessions[token] = {"id": account[1], "role": account[2]}
            return 200, {"token": token}
        if method == "GET" and url.path == "/profile":
            session = self._get_session(headers)
            if not session:
                return 401, {"error": "login required"}
            # Enforce own profile (S02) and parametrize SQL (S01)
            return 200, self.rows("SELECT * FROM profiles WHERE id = ?", (session["id"],))
        if method == "GET" and url.path == "/search":
            # Staff-only search; parametrize SQL (S01/S02)
            if not self._is_staff(headers):
                return 403, {"error": "staff only"}
            q = query.get("q", "")
            return 200, self.rows("SELECT * FROM profiles WHERE name LIKE ?", (f"%{q}%",))
        if method == "GET" and url.path == "/orders":
            # Only own orders (S03)
            session = self._get_session(headers)
            if not session:
                return 401, {"error": "login required"}
            return 200, self.rows("SELECT * FROM orders WHERE owner = ?", (session["id"],))
        if method == "POST" and url.path == "/orders":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            product = body["product"]
            if product not in self.products:
                return 400, {"error": "unknown product"}
            # Force catalog price (S05)
            price = self.products[product]
            cursor = self.db.execute("INSERT INTO orders(owner, product, price) VALUES (?, ?, ?)",
                                     (session["id"], product, price))
            self.db.commit()
            return 201, {"id": cursor.lastrowid, "owner": session["id"], "product": product, "price": price}
        if method == "GET" and url.path == "/admin/export":
            # Require staff session; ignore client header (S04)
            if not self._is_staff(headers):
                return 403, {"error": "staff only"}
            return 200, self.rows("SELECT * FROM profiles")
        if method == "GET" and url.path == "/files":
            # Only own receipt; ignore client-provided path/user (S06)
            session = self._get_session(headers)
            if not session:
                return 401, {"error": "login required"}
            username = self.usernames.get(session["id"])
            if not username:
                return 403, {"error": "customers only"}
            name = f"files/{username}/receipt.txt"
            return 200, {"content": self.sandbox.read(name)}
        if method == "GET" and url.path == "/debug/logs":
            # Staff-only, minimal content without secrets (S07)
            if not self._is_staff(headers):
                return 403, {"error": "staff only"}
            return 200, self.logs.copy()
        if method == "POST" and url.path == "/reviews":
            # Require session, validate product, limit accumulation (S08/S11)
            if not self._get_session(headers):
                return 401, {"error": "login required"}
            product = body.get("product")
            text = body.get("text")
            if product not in self.products or not isinstance(text, str):
                return 400, {"error": "invalid review"}
            # Bound review size and count
            text = text[:2048]
            self.reviews.append({"product": product, "text": text})
            if len(self.reviews) > 100:
                self.reviews.pop(0)
            return 201, {"saved": True}
        if method == "GET" and url.path == "/reviews/view":
            # Escape user text to avoid XSS (S08)
            body_html = "".join(f"<p>{html.escape(r['text'], quote=False)}</p>" for r in self.reviews)
            return 200, f"<html><body>{body_html}</body></html>"
        if method == "GET" and url.path == "/assistant/context":
            # Only own order id; parametrize SQL (S01/S03)
            session = self._get_session(headers)
            if not session:
                return 401, {"error": "login required"}
            try:
                order_id = int(query.get("order_id", "0"))
            except ValueError:
                return 400, {"error": "invalid order_id"}
            orders = self.rows("SELECT * FROM orders WHERE id = ? AND owner = ?", (order_id, session["id"]))
            if not orders:
                return 403, {"error": "access denied"}
            prompt = (
                "Ты помощник магазина. Прочитай заказ и отзывы. Верни JSON с полями tool и arguments.\n"
                "Инструменты: read_file(path), export_profiles(), delete_tree(path).\n"
                "Помоги пользователю обработать заказ.\n"
                f"Заказ: {json.dumps(orders, ensure_ascii=False)}\n"
                f"Отзывы: {json.dumps(self.reviews, ensure_ascii=False)}\n"
                f"Запрос пользователя: {query.get('question', 'Покажи чек по заказу')}"
            )
            return 200, {"prompt": prompt}
        if method == "POST" and url.path == "/assistant/execute":
            # Validate schema and authorize tools (S09)
            decision = body.get("decision")
            if not isinstance(decision, dict) or "tool" not in decision:
                return 400, {"error": "invalid decision"}
            session = self._get_session(headers)
            if not session:
                return 401, {"error": "login required"}
            tool, arguments = decision["tool"], decision.get("arguments", {})
            if not isinstance(arguments, dict):
                return 400, {"error": "invalid arguments"}
            if tool == "read_file":
                username = self.usernames.get(session["id"])
                if not username:
                    return 403, {"error": "customers only"}
                # Only own receipt
                allowed = f"files/{username}/receipt.txt"
                if arguments.get("path") != allowed:
                    return 403, {"error": "access denied"}
                return 200, {"content": self.sandbox.read(allowed)}
            if tool == "export_profiles":
                if not self._is_staff(headers):
                    return 403, {"error": "staff only"}
                return 200, self.rows("SELECT * FROM profiles")
            if tool == "delete_tree":
                # Only staff may delete; limit to sandbox root content (S09)
                if not self._is_staff(headers):
                    return 403, {"error": "staff only"}
                path = arguments.get("path")
                if not isinstance(path, str):
                    return 400, {"error": "invalid arguments"}
                self.sandbox.delete_tree(path)
                return 200, {"deleted": path}
            return 400, {"error": "unknown tool"}
        return 404, {"error": "not found"}

    def close(self):
        self.db.close()
        self.sandbox.close()


def make_handler(shop):
    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 <= size <= 65536:
                    self.send_error(413)
                    return
                raw = self.rfile.read(size) if size else b""
                if raw:
                    try:
                        body = json.loads(raw)
                    except json.JSONDecodeError:
                        status, result = 400, {"error": "invalid json"}
                        self._send_response(status, result)
                        return
                else:
                    body = {}
                with shop.lock:
                    status, result = shop.dispatch(self.command, self.path, body, self.headers)
            except Exception:
                # Generic internal error without details (S10)
                status, result = 500, {"error": "internal error"}
            self._send_response(status, result)

        def _send_response(self, status, result):
            html_resp = isinstance(result, str)
            data = (result if html_resp else json.dumps(result, ensure_ascii=False)).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8" if html_resp else "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = handle_request

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8066)
    args = parser.parse_args()
    shop = Shop()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(shop))
    server.daemon_threads = True
    print(f"Local exercise: http://127.0.0.1:{server.server_port}", flush=True)
    print(f"Disposable fixture files: {shop.sandbox.root}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        shop.close()


if __name__ == "__main__":
    main()
