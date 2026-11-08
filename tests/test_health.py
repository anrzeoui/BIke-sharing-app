"""Container and Kubernetes probes must see a ready application and database."""

import tempfile
import unittest
from pathlib import Path

from bike_sharing import create_app


class HealthTest(unittest.TestCase):
    def test_health_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            app = create_app(
                {"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": str(Path(directory) / "test.db")}
            )
            response = app.test_client().get("/healthz")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"status": "ok"})
