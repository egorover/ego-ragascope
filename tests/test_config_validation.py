# -*- coding: utf-8 -*-
"""Тесты валидации config в изолированном subprocess."""
import subprocess
import sys
import unittest


class TestConfigValidation(unittest.TestCase):
    def _import_config(self, env: dict) -> subprocess.CompletedProcess:
        env_lines = "\n".join(
            f"os.environ[{k!r}] = {v!r}" for k, v in env.items()
        )
        script = f"""
import os
for key in list(os.environ):
    if key.startswith(("API_", "PROXY_", "OPENAI_")):
        del os.environ[key]
{env_lines}
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: False
import importlib
import config
importlib.reload(config)
print(config.API_PROVIDER)
"""
        return subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
        )

    def test_proxy_requires_key(self):
        result = self._import_config(
            {
                "API_PROVIDER": "proxy",
                "PROXY_API_URL": "https://api.example.com/v1",
                "PROXY_API_KEY": "",
                "OPENAI_API_KEY": "",
            }
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PROXY_API_KEY", result.stderr or "")

    def test_openai_requires_key(self):
        result = self._import_config(
            {
                "API_PROVIDER": "openai",
                "OPENAI_API_KEY": "",
                "PROXY_API_KEY": "x",
            }
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OPENAI_API_KEY", result.stderr or "")

    def test_invalid_provider(self):
        result = self._import_config(
            {
                "API_PROVIDER": "unknown",
                "PROXY_API_KEY": "test-key",  # pragma: allowlist secret
                "PROXY_API_URL": "https://api.example.com/v1",
            }
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("API_PROVIDER", result.stderr or "")


if __name__ == "__main__":
    unittest.main()
