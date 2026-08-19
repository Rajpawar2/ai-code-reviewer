import ast
from typing import List, Dict, Any


class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Dict[str, Any]] = []
        self.loop_depth = 0
        self.block_depth = 0

    def analyze(self) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(self.code)
            self.visit(tree)
        except SyntaxError as e:
            self.findings.append({
                "severity": "CRITICAL",
                "category": "ast",
                "title": "Syntax Error",
                "description": f"Python syntax error: {e.msg}",
                "line_number": e.lineno or 1,
                "recommendation": "Fix the syntax error to ensure the code can be executed and parsed.",
                "suggested_code": None
            })
        except Exception as e:
            self.findings.append({
                "severity": "HIGH",
                "category": "ast",
                "title": "AST Parsing Error",
                "description": f"Failed to parse AST: {str(e)}",
                "line_number": 1,
                "recommendation": "Check code structure for invalid Python tokens.",
                "suggested_code": None
            })
        return self.findings

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Check mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append({
                    "severity": "HIGH",
                    "category": "bug",
                    "title": "Mutable Default Argument",
                    "description": f"Function '{node.name}' uses a mutable default argument ({type(default).__name__.lower()}).",
                    "line_number": node.lineno,
                    "recommendation": "Use None as the default argument value and initialize the mutable object inside the function body.",
                    "suggested_code": f"def {node.name}(..., param=None):\n    if param is None:\n        param = {ast.unparse(default)}"
                })

        # 2. Overly large function check
        func_length = (node.end_lineno or node.lineno) - node.lineno + 1
        if func_length > 60:
            self.findings.append({
                "severity": "LOW",
                "category": "maintainability",
                "title": "Overly Large Function",
                "description": f"Function '{node.name}' is {func_length} lines long (> 60 lines), which reduces maintainability and readability.",
                "line_number": node.lineno,
                "recommendation": "Refactor the function by breaking it down into smaller, single-purpose helper functions.",
                "suggested_code": None
            })

        # 3. Check unreachable code in function body
        self._check_unreachable_code(node.body)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # type: ignore

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Bare except check
        if node.type is None:
            self.findings.append({
                "severity": "HIGH",
                "category": "bug",
                "title": "Bare 'except:' Clause",
                "description": "A bare 'except:' clause catches all exceptions including SystemExit and KeyboardInterrupt, masking unexpected errors.",
                "line_number": node.lineno,
                "recommendation": "Catch specific exception types (e.g., 'except Exception:' or 'except ValueError:').",
                "suggested_code": "except Exception as e:"
            })
        # Empty except pass check
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.findings.append({
                "severity": "MEDIUM",
                "category": "quality",
                "title": "Silent Exception Suppression",
                "description": "Exception handler suppresses errors silently with 'pass' without logging or handling.",
                "line_number": node.lineno,
                "recommendation": "Log the exception or handle it appropriately rather than silently ignoring it.",
                "suggested_code": "except Exception as e:\n    logger.error(f'Error occurred: {e}')"
            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Detect eval / exec
        if func_name == "eval":
            self.findings.append({
                "severity": "CRITICAL",
                "category": "security",
                "title": "Dangerous 'eval()' Execution",
                "description": "Usage of eval() allows arbitrary code execution and is a critical security vulnerability.",
                "line_number": node.lineno,
                "recommendation": "Use ast.literal_eval() for safe literal evaluation or parse structured formats like JSON.",
                "suggested_code": "import ast\nresult = ast.literal_eval(untrusted_str)"
            })
        elif func_name == "exec":
            self.findings.append({
                "severity": "CRITICAL",
                "category": "security",
                "title": "Dangerous 'exec()' Execution",
                "description": "Usage of exec() executes dynamic Python code and poses high risk of remote code execution.",
                "line_number": node.lineno,
                "recommendation": "Avoid dynamic code execution. Implement predefined dispatch tables or structured logic instead.",
                "suggested_code": None
            })

        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.loop_depth += 1
        if self.loop_depth >= 3:
            self.findings.append({
                "severity": "MEDIUM",
                "category": "performance",
                "title": "Deeply Nested Loops",
                "description": f"Detected loop nesting depth of {self.loop_depth}. Deeply nested loops lead to O(N^{self.loop_depth}) time complexity.",
                "line_number": node.lineno,
                "recommendation": "Refactor nested loops using lookup dictionaries, hash sets, or itertools.",
                "suggested_code": None
            })
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.loop_depth += 1
        if self.loop_depth >= 3:
            self.findings.append({
                "severity": "MEDIUM",
                "category": "performance",
                "title": "Deeply Nested Loops",
                "description": f"Detected loop nesting depth of {self.loop_depth}. Deeply nested loops lead to exponential/polynomial time complexity.",
                "line_number": node.lineno,
                "recommendation": "Refactor nested loops to optimize algorithmic complexity.",
                "suggested_code": None
            })
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Compare(self, node: ast.Compare):
        # Detect '== None' or '!= None' or '== True' or '== False'
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(comparator, ast.Constant):
                if comparator.value is None and isinstance(op, (ast.Eq, ast.NotEq)):
                    comp_str = "==" if isinstance(op, ast.Eq) else "!="
                    rec_str = "is None" if isinstance(op, ast.Eq) else "is not None"
                    self.findings.append({
                        "severity": "LOW",
                        "category": "quality",
                        "title": f"Comparison to None with '{comp_str}'",
                        "description": f"Comparisons to None should use 'is' or 'is not', not '{comp_str}'.",
                        "line_number": node.lineno,
                        "recommendation": f"Replace with '{rec_str}'.",
                        "suggested_code": f"if variable {rec_str}:"
                    })
                elif isinstance(comparator.value, bool) and isinstance(op, (ast.Eq, ast.NotEq)):
                    self.findings.append({
                        "severity": "LOW",
                        "category": "quality",
                        "title": "Direct Boolean Comparison",
                        "description": "Avoid explicit comparison to True/False constants.",
                        "line_number": node.lineno,
                        "recommendation": "Use truthiness directly: 'if condition:' or 'if not condition:'.",
                        "suggested_code": "if condition:"
                    })
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        dangerous_modules = {
            "telnetlib": ("HIGH", "Insecure communication protocol (telnet is unencrypted)"),
            "ftplib": ("MEDIUM", "FTP sends credentials in plaintext without TLS"),
        }
        for alias in node.names:
            if alias.name in dangerous_modules:
                sev, desc = dangerous_modules[alias.name]
                self.findings.append({
                    "severity": sev,
                    "category": "security",
                    "title": f"Suspicious/Insecure Module Import: {alias.name}",
                    "description": desc,
                    "line_number": node.lineno,
                    "recommendation": "Replace with secure alternatives such as SSH/Paramiko or HTTPS/SFTP.",
                    "suggested_code": None
                })
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        self.findings.append({
            "severity": "LOW",
            "category": "maintainability",
            "title": "Use of 'global' Keyword",
            "description": f"Global variable modification ({', '.join(node.names)}) introduces hidden side effects and state coupling.",
            "line_number": node.lineno,
            "recommendation": "Encapsulate state inside a class or pass values explicitly through parameters and return values.",
            "suggested_code": None
        })
        self.generic_visit(node)

    def _check_unreachable_code(self, statements: List[ast.stmt]):
        for i, stmt in enumerate(statements[:-1]):
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                next_stmt = statements[i + 1]
                self.findings.append({
                    "severity": "MEDIUM",
                    "category": "bug",
                    "title": "Unreachable Code Detected",
                    "description": f"Code following '{type(stmt).__name__.lower()}' on line {stmt.lineno} will never be executed.",
                    "line_number": next_stmt.lineno,
                    "recommendation": "Remove or restructure dead code after return/raise statements.",
                    "suggested_code": None
                })
                break
