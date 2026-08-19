import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any
from app.core.logging import logger


class LintAnalyzer:
    """Runs Ruff programmatically to detect lint errors, code smells, and style issues."""

    def __init__(self, code: str, filename: str = "snippet.py"):
        self.code = code
        self.filename = filename

    def analyze(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(self.code)
            tmp_path = tmp.name

        try:
            cmd = ["ruff", "check", "--output-format=json", tmp_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )

            stdout = result.stdout.strip()
            if not stdout:
                return findings

            try:
                data = json.loads(stdout)
                for item in data:
                    code = item.get("code", "")
                    message = item.get("message", "Lint issue")
                    location = item.get("location", {})
                    row = location.get("row", 1)
                    severity = self._map_severity(code)
                    category = self._map_category(code)

                    findings.append({
                        "severity": severity,
                        "category": category,
                        "title": f"Ruff [{code}]: {message}",
                        "description": f"Rule {code}: {message}",
                        "line_number": row,
                        "recommendation": f"Resolve rule violation {code} according to PEP 8 / Flake8 / Ruff standards.",
                        "suggested_code": None
                    })
            except json.JSONDecodeError:
                logger.warning(f"Could not parse Ruff JSON output: {stdout}")

        except subprocess.TimeoutExpired:
            logger.error("Ruff execution timed out")
        except Exception as e:
            logger.error(f"Error running Ruff analyzer: {e}")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        return findings

    def _map_severity(self, code: str) -> str:
        if code.startswith("F821") or code.startswith("E999"):  # Undefined name / syntax error
            return "CRITICAL"
        elif code.startswith("F") or code.startswith("B"):  # Pyflakes errors / Bugbear
            return "HIGH"
        elif code.startswith("E") or code.startswith("W"):  # Pycodestyle errors/warnings
            return "MEDIUM"
        elif code.startswith("C") or code.startswith("I"):  # Complexity / Import sorting
            return "LOW"
        return "MEDIUM"

    def _map_category(self, code: str) -> str:
        if code.startswith("S"):
            return "security"
        elif code.startswith("F") or code.startswith("B"):
            return "bug"
        elif code.startswith("C"):
            return "complexity"
        elif code.startswith("E") or code.startswith("W"):
            return "quality"
        return "lint"
