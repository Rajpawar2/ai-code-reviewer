from typing import Dict, Any, List, Optional
from app.analyzers.ast_analyzer import ASTAnalyzer
from app.analyzers.lint_analyzer import LintAnalyzer
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.complexity_analyzer import ComplexityAnalyzer
from app.services.scoring_service import ScoringService
from app.ai.base import AIProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.mock_provider import MockAIProvider
from app.core.config import settings
from app.core.logging import logger


class AnalysisService:
    """Orchestrates deterministic analyzers, AI provider review, and scoring calculation."""

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        if ai_provider:
            self.ai_provider = ai_provider
        elif settings.AI_PROVIDER == "mock":
            self.ai_provider = MockAIProvider()
        else:
            self.ai_provider = OllamaProvider()

    async def analyze_code(
        self,
        code: str,
        filename: str = "snippet.py"
    ) -> Dict[str, Any]:
        logger.info(f"Starting analysis for file: {filename}")

        # 1. Deterministic AST Analysis
        ast_analyzer = ASTAnalyzer(code)
        ast_findings = ast_analyzer.analyze()

        # 2. Ruff Lint Analysis
        lint_analyzer = LintAnalyzer(code, filename)
        lint_findings = lint_analyzer.analyze()

        # 3. Bandit Security Analysis
        security_analyzer = SecurityAnalyzer(code, filename)
        security_findings = security_analyzer.analyze()

        # 4. Radon Complexity Analysis
        complexity_analyzer = ComplexityAnalyzer(code, filename)
        complexity_metrics, complexity_findings = complexity_analyzer.analyze()

        # Aggregate all static findings (deduplicate overlapping lines/titles if needed)
        static_findings = ast_findings + lint_findings + security_findings + complexity_findings

        # 5. Compute Deterministic Scores (initially before AI synthesis)
        # 6. AI Review Synthesis via Ollama (or Mock)
        ai_available = True
        ai_review = None
        try:
            ai_review = await self.ai_provider.review_code(
                code=code,
                filename=filename,
                static_findings=static_findings,
                complexity=complexity_metrics
            )
        except Exception as e:
            logger.error(f"AI Provider error during review: {e}")
            ai_available = False

        # Merge AI-detected issues into unified findings list
        merged_findings = list(static_findings)
        if ai_review:
            # Add unique AI bugs
            for bug in ai_review.bugs:
                if not self._is_duplicate(bug.title, bug.line_number, merged_findings):
                    merged_findings.append({
                        "severity": bug.severity,
                        "category": "bug",
                        "title": f"AI [Bug]: {bug.title}",
                        "description": bug.description,
                        "line_number": bug.line_number,
                        "recommendation": bug.recommendation,
                        "suggested_code": bug.suggested_code
                    })

            # Add unique AI security issues
            for sec in ai_review.security_issues:
                if not self._is_duplicate(sec.title, sec.line_number, merged_findings):
                    merged_findings.append({
                        "severity": sec.severity,
                        "category": "security",
                        "title": f"AI [Security]: {sec.title}",
                        "description": sec.description,
                        "line_number": sec.line_number,
                        "recommendation": sec.recommendation,
                        "suggested_code": sec.suggested_code
                    })

            # Add performance issues
            for perf in ai_review.performance_issues:
                if not self._is_duplicate(perf.title, perf.line_number, merged_findings):
                    merged_findings.append({
                        "severity": perf.severity,
                        "category": "performance",
                        "title": f"AI [Performance]: {perf.title}",
                        "description": perf.description,
                        "line_number": perf.line_number,
                        "recommendation": perf.recommendation,
                        "suggested_code": perf.suggested_code
                    })

            # Add quality issues
            for qual in ai_review.code_quality_issues:
                if not self._is_duplicate(qual.title, qual.line_number, merged_findings):
                    merged_findings.append({
                        "severity": qual.severity,
                        "category": "quality",
                        "title": f"AI [Quality]: {qual.title}",
                        "description": qual.description,
                        "line_number": qual.line_number,
                        "recommendation": qual.recommendation,
                        "suggested_code": qual.suggested_code
                    })

            # Add best practices
            for bp in ai_review.best_practices:
                if not self._is_duplicate(bp.title, bp.line_number, merged_findings):
                    merged_findings.append({
                        "severity": bp.severity,
                        "category": "quality",
                        "title": f"AI [Best Practice]: {bp.title}",
                        "description": bp.description,
                        "line_number": bp.line_number,
                        "recommendation": bp.recommendation,
                        "suggested_code": bp.suggested_code
                    })

        # Recalculate deterministic scores with merged findings
        final_scores = ScoringService.calculate_scores(merged_findings, complexity_metrics)

        return {
            "scores": final_scores,
            "complexity": complexity_metrics,
            "findings": merged_findings,
            "ai_available": ai_available,
            "ai_summary": ai_review.summary if ai_review else "AI review unavailable; static analysis completed.",
            "fixed_code": ai_review.fixed_code if ai_review else None
        }

    def _is_duplicate(self, title: str, line_number: int, existing_findings: List[Dict[str, Any]]) -> bool:
        t_clean = title.lower()
        for f in existing_findings:
            if f.get("line_number") == line_number and (t_clean in f.get("title", "").lower() or f.get("title", "").lower() in t_clean):
                return True
        return False
