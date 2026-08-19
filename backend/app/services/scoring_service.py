from typing import List, Dict, Any


class ScoringService:
    """Calculates deterministic quality, security, performance, maintainability, and overall scores."""

    PENALTIES = {
        "CRITICAL": 15.0,
        "HIGH": 8.0,
        "MEDIUM": 4.0,
        "LOW": 1.0,
    }

    @classmethod
    def calculate_scores(cls, findings: List[Dict[str, Any]], complexity_metrics: Dict[str, Any] = None) -> Dict[str, float]:
        overall_score = 100.0
        security_score = 100.0
        quality_score = 100.0
        performance_score = 100.0
        maintainability_score = 100.0

        for finding in findings:
            sev = finding.get("severity", "LOW").upper()
            cat = finding.get("category", "quality").lower()
            penalty = cls.PENALTIES.get(sev, 1.0)

            # Overall deduction
            overall_score -= penalty

            # Category-specific deduction
            if cat == "security":
                security_score -= penalty * 1.5
            elif cat in ("performance",):
                performance_score -= penalty * 1.5
            elif cat in ("maintainability", "complexity"):
                maintainability_score -= penalty * 1.5
            elif cat in ("bug", "ast"):
                quality_score -= penalty * 1.2
                overall_score -= penalty * 0.5  # bugs have strong weight
            else:  # "lint", "quality"
                quality_score -= penalty

        # Incorporate maintainability index if provided
        if complexity_metrics and "maintainability_index" in complexity_metrics:
            mi = complexity_metrics["maintainability_index"]
            # Blend Radon MI into maintainability score
            maintainability_score = (maintainability_score * 0.6) + (mi * 0.4)

        return {
            "overall_score": cls._clamp(overall_score),
            "security_score": cls._clamp(security_score),
            "quality_score": cls._clamp(quality_score),
            "performance_score": cls._clamp(performance_score),
            "maintainability_score": cls._clamp(maintainability_score),
        }

    @staticmethod
    def _clamp(score: float) -> float:
        return round(max(0.0, min(100.0, score)), 1)
