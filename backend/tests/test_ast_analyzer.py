from app.analyzers.ast_analyzer import ASTAnalyzer


def test_mutable_default_argument_detection():
    code = """
def add_item(item, basket=[]):
    basket.append(item)
    return basket
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    assert any("Mutable Default Argument" in f["title"] for f in findings)
    mutable_finding = next(f for f in findings if "Mutable Default Argument" in f["title"])
    assert mutable_finding["severity"] == "HIGH"
    assert mutable_finding["line_number"] == 2


def test_bare_except_detection():
    code = """
try:
    x = 1 / 0
except:
    pass
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    assert any("Bare 'except:'" in f["title"] for f in findings)


def test_eval_exec_detection():
    code = """
user_str = input()
eval(user_str)
exec("import os")
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    critical_titles = [f["title"] for f in findings if f["severity"] == "CRITICAL"]
    assert any("eval()" in t for t in critical_titles)
    assert any("exec()" in t for t in critical_titles)


def test_nested_loops_detection():
    code = """
for i in range(10):
    for j in range(10):
        for k in range(10):
            print(i, j, k)
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    assert any("Deeply Nested Loops" in f["title"] for f in findings)


def test_comparison_to_none():
    code = """
if x == None:
    print("Is None")
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    assert any("Comparison to None" in f["title"] for f in findings)


def test_unreachable_code_detection():
    code = """
def sample():
    return 42
    print("Never reached")
"""
    analyzer = ASTAnalyzer(code)
    findings = analyzer.analyze()
    assert any("Unreachable Code" in f["title"] for f in findings)
