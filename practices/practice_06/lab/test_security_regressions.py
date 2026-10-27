"""Security regression tests for Mini Shop (Practice 06).
These tests assert secure behaviors derived from REPORT_01 and lab/README.
"""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from service import Shop, make_handler


class SecurityRegressionTest(unittest.TestCase):
    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)

    def request(self, method, path, body=None, headers=None):
        with self.shop.lock:
            return self.shop.dispatch(method, path, body or {}, headers or {})

    def login(self, username="alice", password="learn-alice"):
        status, result = self.request("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": result["token"]}

    # S01/S02: Profile/search must be authorized, parameterized, limited
    def test_profile_requires_session_and_returns_own(self):
        self.assertEqual(self.request("GET", "/profile")[0], 401)
        alice = self.login()
        status, profile = self.request("GET", "/profile?id=2", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(profile[0]["id"], 1)

    def test_search_staff_only(self):
        self.assertEqual(self.request("GET", "/search?q=A")[0], 403)
        staff = self.login("staff", "learn-staff")
        status, result = self.request("GET", "/search?q=TEST_", headers=staff)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(result), 1)

    def test_sql_payloads_do_not_expand_results(self):
        alice = self.login()
        status, profiles = self.request("GET", "/profile?id=1%20OR%201=1", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual([p["id"] for p in profiles], [1])
        staff = self.login("staff", "learn-staff")
        status, profiles = self.request("GET", "/search?q=%27%20OR%201=1--", headers=staff)
        self.assertEqual((status, profiles), (200, []))

    def test_assistant_context_requires_owned_order(self):
        self.assertEqual(self.request("GET", "/assistant/context?order_id=1")[0], 401)
        alice = self.login()
        self.assertEqual(self.request("GET", "/assistant/context?order_id=2", headers=alice)[0], 403)
        self.assertEqual(self.request("GET", "/assistant/context?order_id=1%20OR%201=1", headers=alice)[0], 400)
        status, context = self.request("GET", "/assistant/context?order_id=1", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn('"owner": 1', context["prompt"])
        self.assertNotIn('"owner": 2', context["prompt"])

    # S03: Orders limited to owner
    def test_orders_only_own(self):
        self.assertEqual(self.request("GET", "/orders")[0], 401)
        alice, bob = self.login(), self.login("bob", "learn-bob")
        self.assertTrue(all(o["owner"] == 1 for o in self.request("GET", "/orders", headers=alice)[1]))
        self.assertTrue(all(o["owner"] == 2 for o in self.request("GET", "/orders", headers=bob)[1]))

    # S05: Price from catalog only
    def test_order_price_forced_from_catalog(self):
        alice = self.login()
        status, order = self.request("POST", "/orders", {"product": "lamp", "price": 1}, alice)
        self.assertEqual(status, 201)
        self.assertEqual(order["price"], 1500)

    # S04: Export requires staff session, ignores X-Role header
    def test_export_requires_staff_session(self):
        alice_hdrs = {**self.login(), "X-Role": "staff"}
        self.assertEqual(self.request("GET", "/admin/export", headers=alice_hdrs)[0], 403)
        staff = {**self.login("staff", "learn-staff")}
        self.assertEqual(self.request("GET", "/admin/export", headers=staff)[0], 200)

    # S06: Files limited to own receipt
    def test_files_only_own_receipt(self):
        alice = self.login()
        status, result = self.request("GET", "/files?user=bob&path=../../etc/passwd", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", result["content"])  # still own receipt

    # S07: Logs protected and sanitized
    def test_logs_staff_only_and_sanitized(self):
        alice = self.login()
        self.assertEqual(self.request("GET", "/debug/logs", headers=alice)[0], 403)
        staff = self.login("staff", "learn-staff")
        self.request("POST", "/login", {"username": "alice", "password": "learn-alice"})
        status, logs = self.request("GET", "/debug/logs", headers=staff)
        self.assertEqual(status, 200)
        self.assertTrue(all("body" not in entry and "headers" not in entry for entry in logs))

    # S08: Reviews safe HTML
    def test_reviews_escaped_html(self):
        alice = self.login()
        self.assertEqual(self.request("POST", "/reviews", {"product": "chair", "text": "<b>x</b>"}, alice)[0], 201)
        status, html = self.request("GET", "/reviews/view", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)

    # S10: Invalid JSON yields 400, no internal details via HTTP handler
    def test_invalid_json_400(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.shop))
        server.daemon_threads = True
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            req = Request(base + "/orders", data=b"{not a json}", headers={"Content-Type": "application/json"}, method="POST")
            try:
                resp = urlopen(req, timeout=5)
            except HTTPError as exc:
                resp = exc
            with resp:
                body = resp.read().decode()
            self.assertEqual(resp.status, 400)
            self.assertIn("invalid json", body)
            self.assertNotIn("type", body)
        finally:
            server.shutdown()
            t.join(timeout=5)
            server.server_close()

    def test_assistant_execute_rejects_non_object_arguments_over_http(self):
        alice = self.login()
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.shop))
        server.daemon_threads = True
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            for arguments in (None, [], "receipt.txt", 1, True):
                with self.subTest(arguments=arguments):
                    payload = {"decision": {"tool": "read_file", "arguments": arguments}}
                    req = Request(base + "/assistant/execute", data=json.dumps(payload).encode(),
                                  headers={"Content-Type": "application/json", **alice}, method="POST")
                    try:
                        resp = urlopen(req, timeout=5)
                    except HTTPError as exc:
                        resp = exc
                    with resp:
                        body = json.loads(resp.read())
                    self.assertEqual(resp.status, 400)
                    self.assertEqual(body, {"error": "invalid arguments"})
        finally:
            server.shutdown()
            t.join(timeout=5)
            server.server_close()

    # S09: Assistant execute authorization
    def test_assistant_execute_limits_tools(self):
        alice = self.login()
        # read_file only own receipt
        status, result = self.request("POST", "/assistant/execute",
                                      {"decision": {"tool": "read_file", "arguments": {"path": "files/bob/receipt.txt"}}},
                                      alice)
        self.assertEqual(status, 403)
        status, result = self.request("POST", "/assistant/execute",
                                      {"decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}},
                                      alice)
        self.assertEqual(status, 200)
        # export requires staff
        self.assertEqual(self.request("POST", "/assistant/execute",
                                      {"decision": {"tool": "export_profiles"}}, alice)[0], 403)
        staff = self.login("staff", "learn-staff")
        self.assertEqual(self.request("POST", "/assistant/execute",
                                      {"decision": {"tool": "export_profiles"}}, staff)[0], 200)
        # delete_tree requires staff
        self.assertEqual(self.request("POST", "/assistant/execute",
                                      {"decision": {"tool": "delete_tree", "arguments": {"path": "."}}}, alice)[0], 403)

    # S11: Logs ring buffer keeps last 100 entries
    def test_logs_limit_100(self):
        # Generate 120 requests to produce logs with identifiable targets
        for i in range(120):
            self.request("GET", f"/health?i={i}")
        # Access internal logs to avoid adding extra entries via /debug/logs
        logs = self.shop.logs
        self.assertEqual(len(logs), 100)
        # Ensure first retained corresponds to i=20 and last to i=119
        self.assertTrue(logs[0]["target"].endswith("i=20"))
        self.assertTrue(logs[-1]["target"].endswith("i=119"))

    # S11: Reviews ring buffer keeps last 100 entries
    def test_reviews_limit_100(self):
        alice = self.login()
        for i in range(120):
            self.assertEqual(self.request("POST", "/reviews", {"product": "chair", "text": f"r{i}"}, alice)[0], 201)
        status, html = self.request("GET", "/reviews/view", headers=alice)
        self.assertEqual(status, 200)
        # r0..r19 must be absent, r20..r119 present
        self.assertNotIn("r0", html)
        self.assertNotIn("r19", html)
        self.assertIn("r20", html)
        self.assertIn("r119", html)


if __name__ == "__main__":
    unittest.main()
