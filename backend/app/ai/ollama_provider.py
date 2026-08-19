import json
import re
import httpx
from typing import Dict, Any, List, Optional
from app.ai.base import AIProvider, AIReviewResult, AIIssueItem
from app.core.config import settings
from app.core.logging import logger


class OllamaProvider(AIProvider):
    """Communicates with Ollama HTTP API to generate AI code reviews."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(self.model in m for m in models)
                    return {
                        "available": True,
                        "model": self.model,
                        "model_present": model_found,
                        "installed_models": models,
                        "message": f"Ollama is running with model '{self.model}'." if model_found else f"Ollama is running, but '{self.model}' may need to be pulled."
                    }
                else:
                    return {
                        "available": False,
                        "model": self.model,
                        "message": f"Ollama returned HTTP status {res.status_code}."
                    }
        except Exception as e:
            return {
                "available": False,
                "model": self.model,
                "message": f"Ollama is not available: {str(e)}"
            }

    async def review_code(
        self,
        code: str,
        filename: str,
        static_findings: List[Dict[str, Any]],
        complexity: Dict[str, Any]
    ) -> AIReviewResult:
        prompt = self._build_prompt(code, filename, static_findings, complexity)
        
        try:
            # Enforce 45s ceiling so API never leaves client hanging
            raw_response = await self._send_generate_request(prompt)
            parsed = self._extract_and_validate_json(raw_response)
            if parsed:
                return parsed
            logger.warning("Could not parse Ollama JSON. Using deterministic static synthesis fallback.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error communicating with Ollama: status={e.response.status_code}, error={e.response.text}")
        except (httpx.RequestError, httpx.TimeoutException, TimeoutError) as e:
            logger.error(f"Timeout or network error communicating with Ollama: type={type(e).__name__}, details={str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama synthesis: type={type(e).__name__}, details={str(e)}")

        # Fallback to structured review from static analysis if Ollama fails or times out
        logger.warning("Falling back to deterministic AI synthesis due to Ollama timeout/error.")
        return self._generate_fallback_result(code, filename, static_findings, complexity)

    async def _send_generate_request(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 4096,
                "num_predict": 1000
            }
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    def _build_prompt(
        self,
        code: str,
        filename: str,
        static_findings: List[Dict[str, Any]],
        complexity: Dict[str, Any]
    ) -> str:
        findings_summary = json.dumps(static_findings[:10], indent=2)
        complexity_summary = json.dumps(complexity, indent=2)

        # Truncate prompt source code if exceeding 4000 chars / 120 lines
        lines = code.splitlines()
        if len(lines) > 120 or len(code) > 4000:
            prompt_code = "\n".join(lines[:120]) + "\n\n# ... [Remaining lines omitted for analysis prompt efficiency] ..."
        else:
            prompt_code = code

        return f"""You are an expert principal software engineer and secure code auditor specializing in Python.
Analyze the following Python file: '{filename}'.

STATIC ANALYSIS EVIDENCE:
The code was already analyzed with AST, Ruff, Bandit, and Radon tools:
Static Findings:
{findings_summary}

Complexity Metrics:
{complexity_summary}

SOURCE CODE TO REVIEW:
```python
{prompt_code}
```

INSTRUCTIONS:
1. Thoroughly review the code for correctness, security vulnerabilities, performance bottlenecks, code quality, and maintainability.
2. Incorporate and expand upon the static analysis evidence, but verify their validity in context.
3. In 'fixed_code', provide the improved, refactored Python code addressing the main issues identified.
4. Return your entire response as a single, valid JSON object matching this schema:
{{
  "summary": "High level overview of the review and overall code health",
  "bugs": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "title": "Short title",
      "description": "Detailed explanation of the bug",
      "line_number": 1,
      "recommendation": "How to fix it",
      "suggested_code": "code snippet"
    }}
  ],
  "security_issues": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "title": "Short title",
      "description": "Detailed explanation of vulnerability",
      "line_number": 1,
      "recommendation": "Security remediation",
      "suggested_code": "code snippet"
    }}
  ],
  "performance_issues": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "title": "Short title",
      "description": "Performance concern",
      "line_number": 1,
      "recommendation": "Optimization steps",
      "suggested_code": "code snippet"
    }}
  ],
  "code_quality_issues": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "title": "Short title",
      "description": "Code smell / design flaw",
      "line_number": 1,
      "recommendation": "Refactoring suggestion",
      "suggested_code": "code snippet"
    }}
  ],
  "best_practices": [
    {{
      "severity": "LOW",
      "title": "Short title",
      "description": "Idiomatic Python / PEP 8 practice",
      "line_number": 1,
      "recommendation": "Modern Python convention",
      "suggested_code": "code snippet"
    }}
  ],
  "fixed_code": "Complete, working, refactored and secured Python code."
}}
"""

    def _extract_and_validate_json(self, raw_text: str) -> Optional[AIReviewResult]:
        if not raw_text or not raw_text.strip():
            return None

        # Clean JSON markdown fences if present
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        try:
            data = json.loads(text)
            return AIReviewResult.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")
            # Try regex to locate outermost JSON brackets
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    return AIReviewResult.model_validate(data)
                except Exception:
                    pass
            return None

    def _generate_fallback_result(
        self,
        code: str,
        filename: str,
        static_findings: List[Dict[str, Any]],
        complexity: Dict[str, Any]
    ) -> AIReviewResult:
        bugs: List[AIIssueItem] = []
        security_issues: List[AIIssueItem] = []
        performance_issues: List[AIIssueItem] = []
        code_quality_issues: List[AIIssueItem] = []
        best_practices: List[AIIssueItem] = []

        for f in static_findings:
            item = AIIssueItem(
                severity=f.get("severity", "MEDIUM"),
                title=f.get("title", "Static Analysis Issue"),
                description=f.get("description", "Identified by static analyzer"),
                line_number=f.get("line_number", 1),
                recommendation=f.get("recommendation", "Review and fix."),
                suggested_code=f.get("suggested_code")
            )
            cat = f.get("category", "quality")
            if cat in ("bug", "ast"):
                bugs.append(item)
            elif cat == "security":
                security_issues.append(item)
            elif cat == "performance":
                performance_issues.append(item)
            elif cat in ("complexity", "maintainability"):
                code_quality_issues.append(item)
            else:
                best_practices.append(item)

        summary = (
            f"Automated Code Review for '{filename}'. Static analysis detected {len(static_findings)} potential issue(s). "
            f"Maintainability index: {complexity.get('maintainability_index', 'N/A')}. "
            f"(Note: Ollama AI service was unreachable; results synthesized from static tools)."
        )

        return AIReviewResult(
            summary=summary,
            bugs=bugs,
            security_issues=security_issues,
            performance_issues=performance_issues,
            code_quality_issues=code_quality_issues,
            best_practices=best_practices,
            fixed_code=f"# Auto-Refactored fallback\n{code}"
        )
