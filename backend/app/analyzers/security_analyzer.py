import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any
from app.core.logging import logger


class SecurityAnalyzer:
    """Runs Bandit safely to identify common security vulnerabilities without code execution."""

    def __init__(self, code: str, filename: str = "snippet.py"):
        self.code = code
        self.filename = filename

    def analyze(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(self.code)
            tmp_path = tmp.name

        try:
            cmd = ["bandit", "-f", "json", "-q", tmp_path]
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
                results = data.get("results", [])
                for item in results:
                    test_id = item.get("test_id", "")
                    issue_text = item.get("issue_text", "")
                    issue_severity = item.get("issue_severity", "MEDIUM").upper()
                    issue_confidence = item.get("issue_confidence", "MEDIUM")
                    line_number = item.get("line_number", 1)
                    more_info = item.get("more_info", "")

                    severity = self._map_severity(issue_severity)

                    findings.append({
                        "severity": severity,
                        "category": "security",
                        "title": f"Security [{test_id}]: {issue_text}",
                        "description": f"{issue_text} (Severity: {issue_severity}, Confidence: {issue_confidence}). Reference: {more_info}",
                        "line_number": line_number,
                        "recommendation": self._generate_recommendation(test_id, issue_text),
                        "suggested_code": None
                    })
            except json.JSONDecodeError:
                logger.warning(f"Could not parse Bandit JSON output: {stdout}")

        except subprocess.TimeoutExpired:
            logger.error("Bandit execution timed out")
        except Exception as e:
            logger.error(f"Error running Bandit security analyzer: {e}")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        return findings

    def _map_severity(self, bandit_sev: str) -> str:
        if bandit_sev == "HIGH":
            return "CRITICAL"
        elif bandit_sev == "MEDIUM":
            return "HIGH"
        elif bandit_sev == "LOW":
            return "MEDIUM"
        return "LOW"

    def _generate_recommendation(self, test_id: str, issue_text: str) -> str:
        recommendations = {
            "B101": "Do not rely on assert for production validation, as asserts are stripped with python -O optimization.",
            "B102": "Avoid using exec(). Refactor code to use explicit Python callables or data-driven patterns.",
            "B307": "Avoid eval(). Use ast.literal_eval() for safely parsing Python literals from untrusted strings.",
            "B104": "Avoid binding to all interfaces (0.0.0.0) in production unless explicitly intentional.",
            "B105": "Do not hardcode passwords or API keys in source code. Use environment variables.",
            "B106": "Do not hardcode passwords in arguments. Use secrets manager or environment configuration.",
            "B303": "Insecure MD5/SHA1 hash detected. Use SHA-256 (hashlib.sha256) or bcrypt for passwords.",
            "B311": "Standard 'random' is pseudo-random and insecure for cryptography/tokens. Use 'secrets' module.",
            "B602": "Subprocess shell=True poses severe shell injection risk. Use subprocess.run([...], shell=False).",
            "B608": "Possible SQL injection detected. Use parameterized queries or ORM queries instead of string formatting.",
        }
        return recommendations.get(test_id, f"Remediate security issue: {issue_text}")
