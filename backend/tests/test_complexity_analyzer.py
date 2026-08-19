from app.analyzers.complexity_analyzer import ComplexityAnalyzer


def test_radon_complexity_simple():
    code = """
def simple_func(x):
    return x * 2
"""
    analyzer = ComplexityAnalyzer(code)
    metrics, findings = analyzer.analyze()
    assert metrics["lines_of_code"] >= 2
    assert metrics["complexity_level"] == "LOW"
    assert metrics["maintainability_index"] > 75.0


def test_radon_complexity_high():
    code = """
def very_complex_func(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
                    else:
                        return 2
                elif not d:
                    return 3
            elif not c:
                return 4
        elif not b:
            return 5
    elif not a:
        return 6
    return 0
"""
    analyzer = ComplexityAnalyzer(code)
    metrics, findings = analyzer.analyze()
    assert metrics["average_complexity"] >= 5
    assert len(metrics["functions"]) > 0
