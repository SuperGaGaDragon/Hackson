"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import _mount_static_frontend, create_app


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

    def test_startup_starts_derived_worker_when_enabled(self) -> None:
        started: list[tuple[float, int]] = []
        stopped: list[bool] = []

        class FakeSettings:
            static_frontend_dir = None
            derived_worker_enabled = True
            derived_worker_interval_seconds = 0.5
            derived_worker_batch_size = 7

        class FakeLoop:
            def stop(self) -> None:
                stopped.append(True)

        def fake_start(database, *, interval_seconds: float, batch_size: int) -> FakeLoop:
            started.append((interval_seconds, batch_size))
            return FakeLoop()

        with (
            patch("main.get_settings", return_value=FakeSettings()),
            patch("main.connect_mongo"),
            patch("main.close_mongo"),
            patch("main.get_database", return_value=object()),
            patch("main.get_work_mode_service") as get_work_mode_service,
            patch("main.start_derived_worker_loop", side_effect=fake_start),
        ):
            get_work_mode_service.return_value.recover_interrupted_missions.return_value = None
            app = create_app()
            with TestClient(app) as client:
                self.assertEqual(client.get("/health").json(), {"status": "ok"})

        self.assertEqual(started, [(0.5, 7)])
        self.assertEqual(stopped, [True])

    def test_startup_skips_derived_worker_when_disabled(self) -> None:
        class FakeSettings:
            static_frontend_dir = None
            derived_worker_enabled = False
            derived_worker_interval_seconds = 0.5
            derived_worker_batch_size = 7

        with (
            patch("main.get_settings", return_value=FakeSettings()),
            patch("main.connect_mongo"),
            patch("main.close_mongo"),
            patch("main.get_database"),
            patch("main.get_work_mode_service") as get_work_mode_service,
            patch("main.start_derived_worker_loop") as start_loop,
        ):
            get_work_mode_service.return_value.recover_interrupted_missions.return_value = None
            app = create_app()
            with TestClient(app) as client:
                self.assertEqual(client.get("/health").json(), {"status": "ok"})

        start_loop.assert_not_called()

    def test_startup_tolerates_older_work_mode_service_without_recovery_hook(self) -> None:
        class FakeSettings:
            static_frontend_dir = None
            derived_worker_enabled = False
            derived_worker_interval_seconds = 0.5
            derived_worker_batch_size = 7

        with (
            patch("main.get_settings", return_value=FakeSettings()),
            patch("main.connect_mongo"),
            patch("main.close_mongo"),
            patch("main.get_work_mode_service", return_value=object()),
        ):
            app = create_app()
            with TestClient(app) as client:
                self.assertEqual(client.get("/health").json(), {"status": "ok"})
