from app.analyzers.security_analyzer import SecurityAnalyzer


def test_bandit_finds_hardcoded_password():
    code = """
DATABASE_PASSWORD = "HardcodedSecret123!"
def connect():
    pass
"""
    analyzer = SecurityAnalyzer(code)
    findings = analyzer.analyze()
    # Bandit B105 finds hardcoded password string
    assert len(findings) > 0
    assert any(f["category"] == "security" for f in findings)


def test_bandit_finds_subprocess_injection():
    code = """
import subprocess
def ping(host):
    subprocess.Popen(f"ping -c 1 {host}", shell=True)
"""
    analyzer = SecurityAnalyzer(code)
    findings = analyzer.analyze()
    assert any("subprocess" in f["title"].lower() or "shell=true" in f["description"].lower() or "B602" in f["title"] for f in findings)


def test_bandit_clean_code():
    code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    analyzer = SecurityAnalyzer(code)
    findings = analyzer.analyze()
    assert len(findings) == 0
