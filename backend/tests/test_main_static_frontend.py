"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import _mount_static_frontend


class StaticFrontendMountTest(TestCase):
    def test_static_frontend_serves_index_assets_and_route_fallbacks(self) -> None:
        with TemporaryDirectory() as temp_dir:
            frontend_dir = Path(temp_dir)
            assets_dir = frontend_dir / "assets"
            assets_dir.mkdir()
            (frontend_dir / "index.html").write_text("<div id=\"root\"></div>", encoding="utf-8")
            (assets_dir / "app.js").write_text("window.__hackson_test = true;", encoding="utf-8")

            app = FastAPI()
            with patch("main.get_settings") as get_settings:
                get_settings.return_value.static_frontend_dir = str(frontend_dir)
                _mount_static_frontend(app)

            client = TestClient(app)

            self.assertEqual(client.get("/").status_code, 200)
            self.assertIn("root", client.get("/").text)
            self.assertEqual(client.get("/assets/app.js").status_code, 200)
            self.assertIn("hackson_test", client.get("/assets/app.js").text)
            self.assertEqual(client.get("/chat/anything").status_code, 200)
            self.assertIn("root", client.get("/chat/anything").text)
