from typing import List, Dict, Any, Tuple
from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.raw import analyze as analyze_raw
from app.core.logging import logger


class ComplexityAnalyzer:
    """Analyzes Cyclomatic Complexity, Maintainability Index, and Line metrics via Radon."""

    def __init__(self, code: str, filename: str = "snippet.py"):
        self.code = code
        self.filename = filename

    def analyze(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        findings: List[Dict[str, Any]] = []
        metrics: Dict[str, Any] = {
            "lines_of_code": 0,
            "sloc": 0,
            "comments": 0,
            "complexity_level": "LOW",
            "maintainability_index": 100.0,
            "maintainability_rank": "A",
            "average_complexity": 1.0,
            "functions": []
        }

        try:
            # 1. Raw metrics
            raw = analyze_raw(self.code)
            metrics["lines_of_code"] = raw.loc
            metrics["sloc"] = raw.sloc
            metrics["comments"] = raw.comments

            # 2. Maintainability Index
            try:
                mi = mi_visit(self.code, multi=True)
                metrics["maintainability_index"] = round(mi, 2)
                metrics["maintainability_rank"] = mi_rank(mi)
                if mi < 50:
                    findings.append({
                        "severity": "HIGH",
                        "category": "maintainability",
                        "title": f"Low Maintainability Index ({round(mi, 1)}/100)",
                        "description": f"The codebase has a Maintainability Index of {round(mi, 1)} (Rank {metrics['maintainability_rank']}), indicating difficult maintenance.",
                        "line_number": 1,
                        "recommendation": "Refactor complex functions, reduce nested blocks, and eliminate code duplication.",
                        "suggested_code": None
                    })
            except Exception as e:
                logger.warning(f"Error computing Maintainability Index: {e}")

            # 3. Cyclomatic Complexity
            blocks = cc_visit(self.code)
            total_cc = 0
            max_cc = 1

            for block in blocks:
                cc = block.complexity
                rank = cc_rank(cc)
                total_cc += cc
                if cc > max_cc:
                    max_cc = cc

                metrics["functions"].append({
                    "name": block.name,
                    "type": block.letter,
                    "complexity": cc,
                    "rank": rank,
                    "line_number": block.lineno
                })

                if cc >= 15:
                    findings.append({
                        "severity": "CRITICAL" if cc >= 25 else "HIGH",
                        "category": "complexity",
                        "title": f"High Cyclomatic Complexity in '{block.name}' (CC = {cc})",
                        "description": f"Block '{block.name}' on line {block.lineno} has cyclomatic complexity of {cc} (Rank {rank}). High complexity causes bugs and makes testing difficult.",
                        "line_number": block.lineno,
                        "recommendation": "Decompose this function into smaller, single-responsibility functions.",
                        "suggested_code": None
                    })
                elif cc >= 8:
                    findings.append({
                        "severity": "MEDIUM",
                        "category": "complexity",
                        "title": f"Moderate Cyclomatic Complexity in '{block.name}' (CC = {cc})",
                        "description": f"Block '{block.name}' on line {block.lineno} has cyclomatic complexity of {cc} (Rank {rank}).",
                        "line_number": block.lineno,
                        "recommendation": "Consider simplifying control flow and decision paths.",
                        "suggested_code": None
                    })

            if blocks:
                metrics["average_complexity"] = round(total_cc / len(blocks), 2)
            else:
                metrics["average_complexity"] = 1.0

            if max_cc >= 20:
                metrics["complexity_level"] = "CRITICAL"
            elif max_cc >= 10:
                metrics["complexity_level"] = "HIGH"
            elif max_cc >= 5:
                metrics["complexity_level"] = "MEDIUM"
            else:
                metrics["complexity_level"] = "LOW"

        except Exception as e:
            logger.error(f"Error in ComplexityAnalyzer: {e}")

        return metrics, findings
