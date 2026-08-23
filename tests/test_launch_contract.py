import ast
import re
import unittest
from pathlib import Path

# Obsolete when every launch surface is generated from one authoritative configuration.

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def server_bind() -> tuple[str, int]:
    tree = ast.parse(read("proxy/server.py"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "app"
        and node.func.attr == "run"
    ]
    if len(calls) != 1:
        raise AssertionError(f"expected one explicit app.run call, found {len(calls)}")
    kwargs = {keyword.arg: ast.literal_eval(keyword.value) for keyword in calls[0].keywords}
    return kwargs["host"], kwargs["port"]


def capture(pattern: str, text: str, surface: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if match is None:
        raise AssertionError(f"could not find launch contract in {surface}")
    return match.group(1)


class LaunchContractTests(unittest.TestCase):
    def test_server_is_loopback_only_and_has_no_wildcard_cors(self):
        host, port = server_bind()
        server = read("proxy/server.py")

        self.assertEqual((host, port), ("127.0.0.1", 8770))
        self.assertNotIn("CORS(app)", server)
        self.assertNotIn("flask_cors", server)

    def test_every_user_and_runtime_surface_agrees_on_port_8770(self):
        _host, port = server_bind()
        expected_url = f"http://localhost:{port}"
        surfaces = {
            "README.md": (
                read("README.md"),
                r"^Then open \*\*(http://localhost:\d+)\*\* in Firefox\.$",
            ),
            "run.bat": (
                read("run.bat"),
                r"^echo   Proxy running at (http://localhost:\d+)$",
            ),
            "web/index.html": (
                read("web/index.html"),
                r'^const PROXY_URL = "(http://localhost:\d+)";$',
            ),
            "docs/adr/0001-launchable-via-launcher-spell.md": (
                read("docs/adr/0001-launchable-via-launcher-spell.md"),
                r"^- \*\*Browser URL:\*\* `(http://localhost:\d+)`$",
            ),
        }

        for name, (text, pattern) in surfaces.items():
            with self.subTest(surface=name):
                self.assertEqual(capture(pattern, text, name), expected_url)
                self.assertNotIn("localhost:8765", text)

        server = read("proxy/server.py")
        self.assertIn(f"starting on {expected_url}", server)
        adr = surfaces["docs/adr/0001-launchable-via-launcher-spell.md"][0]
        self.assertEqual(
            capture(r"^- \*\*Port hint:\*\* `(\d+)`", adr, "ADR port hint"),
            str(port),
        )


if __name__ == "__main__":
    unittest.main()
