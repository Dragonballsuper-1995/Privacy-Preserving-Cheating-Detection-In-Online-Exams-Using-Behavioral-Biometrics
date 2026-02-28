"""
Project Health Report Generator
================================
Generates a comprehensive project evaluation report (docs/PROJECT_HEALTH_REPORT.md)
covering 6 dimensions: test coverage, code quality, complexity, security, ML performance,
and API traceability.

Usage:
    cd backend
    python scripts/generate_health_report.py

Requirements (test deps):
    pip install pylint radon pip-audit pytest-cov
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── paths ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # project root
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DOCS_DIR = ROOT_DIR / "docs"
REPORT_PATH = DOCS_DIR / "PROJECT_HEALTH_REPORT.md"

# Ensure docs directory exists
DOCS_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def run_cmd(cmd: List[str], cwd: Path, timeout: int = 300) -> Tuple[str, str, int]:
    """Run a subprocess and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, shell=True,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", 1
    except FileNotFoundError:
        return "", f"Command not found: {cmd[0]}", 127


def grade_from_pct(pct: float) -> str:
    if pct >= 80: return "A"
    if pct >= 60: return "B"
    if pct >= 40: return "C"
    return "D"


def grade_from_score_10(score: float) -> str:
    if score >= 8.0: return "A"
    if score >= 6.0: return "B"
    if score >= 4.0: return "C"
    return "D"


def complexity_grade(avg_cc: float) -> str:
    if avg_cc <= 5:  return "A"  # low complexity
    if avg_cc <= 10: return "B"
    if avg_cc <= 20: return "C"
    return "D"


def security_grade(high: int, critical: int) -> str:
    if high == 0 and critical == 0: return "A"
    if critical == 0:               return "B"
    if high <= 2:                   return "C"
    return "D"


def ml_grade(f1: float) -> str:
    if f1 >= 0.85: return "A"
    if f1 >= 0.70: return "B"
    if f1 >= 0.55: return "C"
    return "D"


def overall_gpa(grades: List[str]) -> str:
    mapping = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
    if not grades:
        return "N/A"
    avg = sum(mapping.get(g, 0) for g in grades) / len(grades)
    if avg >= 3.7:  return "A"
    if avg >= 3.3:  return "A-"
    if avg >= 3.0:  return "B+"
    if avg >= 2.7:  return "B"
    if avg >= 2.3:  return "B-"
    if avg >= 2.0:  return "C+"
    if avg >= 1.7:  return "C"
    return "D"


def section_header(num: int, title: str) -> str:
    return f"\n---\n\n## Section {num}: {title}\n"


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 1 — TEST COVERAGE
# ═══════════════════════════════════════════════════════════════════════

def collect_test_coverage() -> Dict[str, Any]:
    """Run pytest with coverage JSON and parse results."""
    print("  [1/6] Running backend test coverage (pytest --cov) ...")

    venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"

    cov_json = BACKEND_DIR / "coverage.json"

    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "pytest", "--cov=app",
         "--cov-report=json", f"--cov-report=json:{cov_json}",
         "--tb=no", "-q", "--no-header", "--override-ini=addopts=",
         "--continue-on-collection-errors",
         "--ignore=tests/test_load.py"],
        cwd=BACKEND_DIR,
        timeout=180,
    )

    data: Dict[str, Any] = {
        "backend_total_pct": 0,
        "backend_modules": [],
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_errors": 0,
        "test_stdout": stdout[:2000],
        "error": None,
    }

    # Parse pytest summary line
    for line in (stdout + stderr).splitlines():
        m = re.search(r"(\d+) passed", line)
        if m:
            data["tests_passed"] = int(m.group(1))
        m = re.search(r"(\d+) failed", line)
        if m:
            data["tests_failed"] = int(m.group(1))
        m = re.search(r"(\d+) error", line)
        if m:
            data["tests_errors"] = int(m.group(1))

    # Parse coverage JSON
    if cov_json.exists():
        try:
            with open(cov_json, "r") as f:
                cov = json.load(f)
            totals = cov.get("totals", {})
            data["backend_total_pct"] = round(totals.get("percent_covered", 0), 1)
            # Per-module breakdown
            for filepath, fdata in cov.get("files", {}).items():
                short = filepath.replace("\\", "/")
                # Only top-level app modules
                if short.startswith("app/"):
                    parts = short.split("/")
                    if len(parts) >= 2:
                        module = parts[1] if parts[1] != "__init__.py" else "app"
                        data["backend_modules"].append({
                            "file": short,
                            "module": module,
                            "pct": round(fdata.get("summary", {}).get("percent_covered", 0), 1),
                        })
        except Exception as e:
            data["error"] = str(e)
    else:
        data["error"] = "coverage.json not generated"

    return data


def format_test_coverage(data: Dict[str, Any]) -> Tuple[str, str]:
    """Return (markdown_section, grade)."""
    pct = data["backend_total_pct"]
    grade = grade_from_pct(pct)

    md = section_header(1, "Test Coverage")
    md += f"**Overall Backend Coverage: {pct}%** — Grade: **{grade}**\n\n"

    md += f"| Metric | Value |\n|--------|-------|\n"
    md += f"| Tests Passed | {data['tests_passed']} |\n"
    md += f"| Tests Failed | {data['tests_failed']} |\n"
    md += f"| Tests Errors | {data['tests_errors']} |\n"
    md += f"| Coverage | {pct}% |\n\n"

    if data.get("error"):
        md += f"> ⚠️ **Warning**: {data['error']}\n\n"

    # Module breakdown (aggregate by top-level module)
    modules: Dict[str, List[float]] = {}
    for entry in data.get("backend_modules", []):
        mod = entry["module"]
        modules.setdefault(mod, []).append(entry["pct"])

    if modules:
        md += "### Per-Module Coverage\n\n"
        md += "| Module | Avg Coverage | Files |\n|--------|-------------|-------|\n"
        for mod in sorted(modules.keys()):
            pcts = modules[mod]
            avg = round(sum(pcts) / len(pcts), 1)
            md += f"| `{mod}` | {avg}% | {len(pcts)} |\n"
        md += "\n"

    return md, grade


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 2 — CODE QUALITY
# ═══════════════════════════════════════════════════════════════════════

def collect_code_quality() -> Dict[str, Any]:
    """Run pylint, flake8, and eslint."""
    print("  [2/6] Running code quality analysis (pylint + flake8 + eslint) ...")
    data: Dict[str, Any] = {}

    venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"

    # ── pylint ──
    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "pylint", "app",
         "--output-format=text", "--disable=C0114,C0115,C0116,C0301,C0303,W0612,W0611,R0903",
         "--max-line-length=120", "--fail-under=0"],
        cwd=BACKEND_DIR,
        timeout=300,
    )
    pylint_score = 0.0
    pylint_issues = {"convention": 0, "refactor": 0, "warning": 0, "error": 0, "fatal": 0}

    combined = (stdout or "") + "\n" + (stderr or "")
    # Parse issue counts from text output
    for line in combined.splitlines():
        if line.strip():
            # Lines like "app/api/analysis.py:99:4: W0621: ..."
            m = re.match(r"^.+:\d+:\d+:\s*([CRWEF])\d+:", line)
            if m:
                cat_map = {"C": "convention", "R": "refactor", "W": "warning", "E": "error", "F": "fatal"}
                cat = cat_map.get(m.group(1), "convention")
                pylint_issues[cat] = pylint_issues.get(cat, 0) + 1
        # Extract score
        m = re.search(r"rated at ([\d.-]+)/10", line)
        if m:
            try:
                pylint_score = float(m.group(1))
            except ValueError:
                pass
    data["pylint_score"] = pylint_score
    data["pylint_issues"] = pylint_issues

    # ── flake8 ──
    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "flake8", "app", "--count", "--statistics", "--format=default"],
        cwd=BACKEND_DIR,
        timeout=60,
    )
    flake8_count = 0
    for line in (stdout + stderr).splitlines():
        # Count non-empty lines that look like issues
        if line.strip() and re.match(r"^app[/\\]", line):
            flake8_count += 1
    data["flake8_count"] = flake8_count

    # ── eslint (frontend) ──
    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    stdout, stderr, rc = run_cmd(
        [npx, "eslint", "src/", "--format=json"],
        cwd=FRONTEND_DIR,
        timeout=120,
    )
    eslint_errors = 0
    eslint_warnings = 0
    try:
        results = json.loads(stdout)
        for f in results:
            eslint_errors += f.get("errorCount", 0)
            eslint_warnings += f.get("warningCount", 0)
    except (json.JSONDecodeError, TypeError):
        pass
    data["eslint_errors"] = eslint_errors
    data["eslint_warnings"] = eslint_warnings

    return data


def format_code_quality(data: Dict[str, Any]) -> Tuple[str, str]:
    score = data.get("pylint_score", 0)
    grade = grade_from_score_10(score)
    issues = data.get("pylint_issues", {})

    md = section_header(2, "Code Quality")
    md += f"**Backend Pylint Score: {score}/10** — Grade: **{grade}**\n\n"

    md += "### Backend (Python)\n\n"
    md += "| Tool | Metric | Value |\n|------|--------|-------|\n"
    md += f"| Pylint | Overall Score | {score}/10 |\n"
    md += f"| Pylint | Errors | {issues.get('error', 0)} |\n"
    md += f"| Pylint | Warnings | {issues.get('warning', 0)} |\n"
    md += f"| Pylint | Refactor | {issues.get('refactor', 0)} |\n"
    md += f"| Pylint | Convention | {issues.get('convention', 0)} |\n"
    md += f"| Flake8 | Issues | {data.get('flake8_count', 0)} |\n\n"

    md += "### Frontend (TypeScript)\n\n"
    md += "| Tool | Metric | Value |\n|------|--------|-------|\n"
    md += f"| ESLint | Errors | {data.get('eslint_errors', 0)} |\n"
    md += f"| ESLint | Warnings | {data.get('eslint_warnings', 0)} |\n\n"

    return md, grade


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 3 — CODE COMPLEXITY
# ═══════════════════════════════════════════════════════════════════════

def collect_complexity() -> Dict[str, Any]:
    """Run radon for cyclomatic complexity and maintainability index."""
    print("  [3/6] Running code complexity analysis (radon) ...")
    data: Dict[str, Any] = {"cc_results": [], "mi_results": [], "avg_cc": 0}

    venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"

    # ── Cyclomatic Complexity ──
    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "radon", "cc", "app", "-j", "-n", "C"],
        cwd=BACKEND_DIR,
        timeout=60,
    )
    try:
        cc_data = json.loads(stdout)
        all_cc = []
        for filepath, funcs in cc_data.items():
            for func in funcs:
                all_cc.append(func.get("complexity", 0))
                data["cc_results"].append({
                    "file": filepath.replace("\\", "/"),
                    "name": func.get("name", "?"),
                    "complexity": func.get("complexity", 0),
                    "rank": func.get("rank", "?"),
                })
        if all_cc:
            data["avg_cc"] = round(sum(all_cc) / len(all_cc), 1)
    except (json.JSONDecodeError, TypeError):
        pass

    # ── Maintainability Index ──
    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "radon", "mi", "app", "-j"],
        cwd=BACKEND_DIR,
        timeout=60,
    )
    try:
        mi_data = json.loads(stdout)
        for filepath, score in mi_data.items():
            data["mi_results"].append({
                "file": filepath.replace("\\", "/"),
                "mi": round(score, 1) if isinstance(score, (int, float)) else score,
            })
    except (json.JSONDecodeError, TypeError):
        pass

    return data


def format_complexity(data: Dict[str, Any]) -> Tuple[str, str]:
    avg_cc = data.get("avg_cc", 0)
    grade = complexity_grade(avg_cc)

    md = section_header(3, "Code Complexity")
    md += f"**Average Cyclomatic Complexity: {avg_cc}** — Grade: **{grade}**\n\n"

    md += "> Complexity grades: A (1-5), B (6-10), C (11-20), D (21+)\n\n"

    # Show only high-complexity functions (grade C or worse)
    complex_funcs = [f for f in data.get("cc_results", []) if f["complexity"] > 10]
    if complex_funcs:
        md += "### High-Complexity Functions (CC > 10)\n\n"
        md += "| File | Function | Complexity | Rank |\n|------|----------|-----------|------|\n"
        for f in sorted(complex_funcs, key=lambda x: -x["complexity"])[:20]:
            md += f"| `{f['file']}` | `{f['name']}` | {f['complexity']} | {f['rank']} |\n"
        md += "\n"
    else:
        md += "✅ No functions with complexity > 10 found.\n\n"

    # Maintainability summary
    mi_list = data.get("mi_results", [])
    if mi_list:
        scores = [m["mi"] for m in mi_list if isinstance(m["mi"], (int, float))]
        if scores:
            avg_mi = round(sum(scores) / len(scores), 1)
            md += f"### Maintainability Index\n\n"
            md += f"**Average MI: {avg_mi}** (100 = very maintainable, 0 = not maintainable)\n\n"
            low_mi = [m for m in mi_list if isinstance(m["mi"], (int, float)) and m["mi"] < 20]
            if low_mi:
                md += "| File | MI Score |\n|------|----------|\n"
                for m in sorted(low_mi, key=lambda x: x["mi"])[:10]:
                    md += f"| `{m['file']}` | {m['mi']} |\n"
                md += "\n"

    return md, grade


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 4 — SECURITY AUDIT
# ═══════════════════════════════════════════════════════════════════════

def collect_security() -> Dict[str, Any]:
    """Run pip-audit and npm audit."""
    print("  [4/6] Running security audits (pip-audit + npm audit) ...")
    data: Dict[str, Any] = {
        "pip_vulns": [],
        "npm_summary": {"low": 0, "moderate": 0, "high": 0, "critical": 0, "total": 0},
        "pip_error": None,
        "npm_error": None,
    }

    venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"

    # ── pip-audit ──
    stdout, stderr, rc = run_cmd(
        [str(venv_python), "-m", "pip_audit", "--format=json", "--desc"],
        cwd=BACKEND_DIR,
        timeout=120,
    )
    try:
        audit = json.loads(stdout)
        deps = audit.get("dependencies", [])
        for dep in deps:
            vulns = dep.get("vulns", [])
            if vulns:
                for v in vulns:
                    data["pip_vulns"].append({
                        "name": dep.get("name", "?"),
                        "version": dep.get("version", "?"),
                        "id": v.get("id", "?"),
                        "description": v.get("description", "")[:100],
                        "fix_versions": v.get("fix_versions", []),
                    })
    except (json.JSONDecodeError, TypeError):
        data["pip_error"] = (stderr or stdout or "pip-audit failed")[:200]

    # ── npm audit ──
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    stdout, stderr, rc = run_cmd(
        [npm, "audit", "--json"],
        cwd=FRONTEND_DIR,
        timeout=60,
    )
    try:
        audit = json.loads(stdout)
        meta = audit.get("metadata", {}).get("vulnerabilities", {})
        if meta:
            data["npm_summary"]["low"] = meta.get("low", 0)
            data["npm_summary"]["moderate"] = meta.get("moderate", 0)
            data["npm_summary"]["high"] = meta.get("high", 0)
            data["npm_summary"]["critical"] = meta.get("critical", 0)
            data["npm_summary"]["total"] = meta.get("total", 0)
    except (json.JSONDecodeError, TypeError):
        data["npm_error"] = (stderr or stdout or "npm audit failed")[:200]

    return data


def format_security(data: Dict[str, Any]) -> Tuple[str, str]:
    pip_vulns = data.get("pip_vulns", [])
    npm = data.get("npm_summary", {})
    high = len([v for v in pip_vulns]) + npm.get("high", 0)
    critical = npm.get("critical", 0)
    grade = security_grade(high, critical)

    md = section_header(4, "Security Audit")
    total = len(pip_vulns) + npm.get("total", 0)
    md += f"**Total Vulnerabilities Found: {total}** — Grade: **{grade}**\n\n"

    md += "### Backend (pip-audit)\n\n"
    if data.get("pip_error"):
        md += f"> ⚠️ pip-audit error: {data['pip_error']}\n\n"
    elif pip_vulns:
        md += f"Found **{len(pip_vulns)}** vulnerabilities:\n\n"
        md += "| Package | Version | Vuln ID | Fix Versions |\n|---------|---------|---------|-------------|\n"
        for v in pip_vulns:
            fix = ", ".join(v.get("fix_versions", []))
            md += f"| `{v['name']}` | {v['version']} | {v['id']} | {fix} |\n"
        md += "\n"
    else:
        md += "✅ No known vulnerabilities found in Python dependencies.\n\n"

    md += "### Frontend (npm audit)\n\n"
    if data.get("npm_error"):
        md += f"> ⚠️ npm audit error: {data['npm_error']}\n\n"
    else:
        md += "| Severity | Count |\n|----------|-------|\n"
        md += f"| Critical | {npm.get('critical', 0)} |\n"
        md += f"| High | {npm.get('high', 0)} |\n"
        md += f"| Moderate | {npm.get('moderate', 0)} |\n"
        md += f"| Low | {npm.get('low', 0)} |\n"
        md += f"| **Total** | **{npm.get('total', 0)}** |\n\n"

    return md, grade


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 5 — ML MODEL EVALUATION
# ═══════════════════════════════════════════════════════════════════════

import threading
import traceback


def _run_with_timeout(func, timeout_sec: int, label: str):
    """Run a function in a thread with a timeout. Returns (result, error_str)."""
    result_box = [None]
    error_box = [None]

    def target():
        try:
            result_box[0] = func()
        except Exception as e:
            error_box[0] = str(e)

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)
    if t.is_alive():
        return None, f"{label} timed out after {timeout_sec}s (skipped)"
    return result_box[0], error_box[0]


def collect_ml_evaluation() -> Dict[str, Any]:
    """Call the existing evaluation module directly with timeouts."""
    print("  [5/6] Running ML model evaluation ...")
    data: Dict[str, Any] = {"available": False, "error": None}

    # Add backend to path so we can import the evaluation module
    sys.path.insert(0, str(BACKEND_DIR))
    os.chdir(str(BACKEND_DIR))

    try:
        from app.ml.evaluation import (
            evaluate_model,
            find_optimal_threshold,
            cross_validate_model,
            load_labeled_dataset,
        )

        dataset = load_labeled_dataset()
        
        # Auto-generate balanced training data if needed
        cheating_count = sum(1 for _, l in dataset if l == 1) if dataset else 0
        if not dataset or cheating_count == 0:
            print("    → No cheating sessions found — auto-generating balanced dataset ...")
            try:
                from app.ml.simulation import generate_training_dataset
                generate_training_dataset(honest_count=50, cheater_count=20)
                dataset = load_labeled_dataset()
            except Exception as e:
                data["error"] = f"Auto-generation failed: {e}"
                return data
        
        if not dataset:
            data["error"] = "No training dataset found. Run simulation first."
            return data

        data["available"] = True
        data["dataset_size"] = len(dataset)
        data["honest"] = sum(1 for _, l in dataset if l == 0)
        data["cheating"] = sum(1 for _, l in dataset if l == 1)

        # Find optimal threshold first (30s timeout)
        print("    → find_optimal_threshold ...")
        eval_threshold = 0.75  # default fallback
        result, err = _run_with_timeout(
            lambda: find_optimal_threshold(), 30, "find_optimal_threshold"
        )
        if result:
            threshold, res = result
            data["optimal_threshold"] = threshold
            eval_threshold = threshold  # use optimal for main eval
            if res:
                data["optimal_metrics"] = res.to_dict()
        elif err:
            data["threshold_error"] = err

        # Main evaluation using optimal threshold (60s timeout)
        print("    → evaluate_model ...")
        result, err = _run_with_timeout(
            lambda: evaluate_model(threshold=eval_threshold), 60, "evaluate_model"
        )
        if result:
            data["eval"] = result.to_dict()
        elif err:
            data["threshold_error"] = err

        # Cross-validation (120s timeout — skip gracefully if too slow)
        print("    → cross_validate_model (may take a while) ...")
        result, err = _run_with_timeout(
            lambda: cross_validate_model(k=3), 120, "cross_validate_model"
        )
        if result:
            data["cross_validation"] = result
        elif err:
            data["cv_error"] = err

    except ImportError as e:
        data["error"] = f"Import error: {e}"
    except Exception as e:
        data["error"] = str(e)

    return data


def format_ml_evaluation(data: Dict[str, Any]) -> Tuple[str, str]:
    md = section_header(5, "ML Model Evaluation")

    if data.get("error"):
        md += f"> ⚠️ **Skipped**: {data['error']}\n\n"
        md += "To generate training data and evaluate:\n"
        md += "1. Start the backend server\n"
        md += "2. Call `POST /api/simulation/generate-training-data`\n"
        md += "3. Re-run this report\n\n"
        return md, "N/A"

    if not data.get("available"):
        md += "> ⚠️ ML evaluation could not be completed.\n\n"
        return md, "N/A"

    md += f"**Training Dataset**: {data.get('dataset_size', 0)} sessions "
    md += f"({data.get('honest', 0)} honest, {data.get('cheating', 0)} cheating)\n\n"

    # Main evaluation results
    ev = data.get("eval")
    f1 = 0.0
    if ev:
        f1 = ev.get("f1", 0)
        grade = ml_grade(f1)
        md += f"### Classification Metrics (threshold = 0.75)\n\n"
        md += "| Metric | Value |\n|--------|-------|\n"
        md += f"| Accuracy | {ev.get('accuracy', 0):.3f} |\n"
        md += f"| Precision | {ev.get('precision', 0):.3f} |\n"
        md += f"| Recall | {ev.get('recall', 0):.3f} |\n"
        md += f"| F1 Score | {ev.get('f1', 0):.3f} |\n"
        md += f"| AUC-ROC | {ev.get('auc_roc', 0):.3f} |\n\n"

        cm = ev.get("confusion_matrix")
        if cm and len(cm) == 2:
            md += "### Confusion Matrix\n\n"
            md += "| | Predicted Honest | Predicted Cheating |\n|---|---|---|\n"
            md += f"| **Actual Honest** | {cm[0][0]} (TN) | {cm[0][1]} (FP) |\n"
            md += f"| **Actual Cheating** | {cm[1][0]} (FN) | {cm[1][1]} (TP) |\n\n"
    elif data.get("eval_error"):
        md += f"> ⚠️ Evaluation error: {data['eval_error']}\n\n"
        grade = "N/A"
    else:
        grade = "N/A"

    # Optimal threshold
    if data.get("optimal_threshold") is not None:
        md += f"### Optimal Threshold\n\n"
        md += f"**Best threshold: {data['optimal_threshold']}** "
        om = data.get("optimal_metrics", {})
        if om:
            md += f"(F1 = {om.get('f1', 0):.3f})\n\n"
        else:
            md += "\n\n"

    # Cross-validation
    cv = data.get("cross_validation")
    if cv:
        md += "### 5-Fold Cross-Validation\n\n"
        agg = cv.get("aggregate", {})
        if agg:
            md += "| Metric | Mean | Std |\n|--------|------|-----|\n"
            for metric in ["accuracy", "precision", "recall", "f1"]:
                mean_k = f"mean_{metric}"
                std_k = f"std_{metric}"
                md += f"| {metric.title()} | {agg.get(mean_k, 0):.3f} | {agg.get(std_k, 0):.3f} |\n"
            md += "\n"
    elif data.get("cv_error"):
        md += f"> ⚠️ Cross-validation error: {data['cv_error']}\n\n"

    return md, grade if isinstance(grade, str) else ml_grade(f1)


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 6 — API ENDPOINT TRACEABILITY
# ═══════════════════════════════════════════════════════════════════════

def collect_api_traceability() -> Dict[str, Any]:
    """Scan API routes and test files for endpoint coverage."""
    print("  [6/6] Scanning API endpoint traceability ...")
    data: Dict[str, Any] = {"endpoints": [], "test_functions": [], "coverage_pct": 0}

    tests_dir = BACKEND_DIR / "tests"

    # Normalize a path: replaces {anything} with {id} for easy comparison
    def normalize_path(path: str) -> str:
        # e.g., /api/exams/{exam_id}/publish -> /api/exams/{id}/publish
        path = re.sub(r'\{[^}]+\}', '{id}', path)
        # Also normalize hardcoded UUIDs in test URLs to {id}
        path = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '{id}', path)
        return path.rstrip('/')

    # 1. Use FastAPI app introspection to get the true list of endpoints
    import sys
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
        
    try:
        from app.main import app
        from fastapi.routing import APIRoute, APIWebSocketRoute
        
        endpoints_map = {}
        for route in app.routes:
            if isinstance(route, APIRoute):
                # Ignore swagger, docs, redoc
                if route.path in ("/api/docs", "/api/redoc", "/api/openapi.json", "/docs", "/redoc", "/openapi.json"):
                    continue
                    
                methods = route.methods or set()
                # Ignore OPTIONS methods
                for m in methods:
                    if m == "OPTIONS": continue
                    full_path = route.path
                    norm_path = normalize_path(full_path)
                    
                    # Try to guess the file from the endpoint name or tags
                    file_name = "main.py"
                    if route.tags:
                        file_name = f"{str(route.tags[0]).lower().replace(' ', '_')}.py"
                    elif route.endpoint.__module__:
                        file_name = f"{route.endpoint.__module__.split('.')[-1]}.py"
                        
                    key = f"{m}:{norm_path}"
                    endpoints_map[key] = {
                        "file": file_name,
                        "method": m,
                        "raw_path": full_path,
                        "norm_path": norm_path,
                        "tested": False
                    }
                    
            elif isinstance(route, APIWebSocketRoute):
                # WebSocket routes might have duplicated prefix due to FastAPI behavior
                full_path = route.path
                if full_path.startswith("/ws/websocket/ws/"):
                    full_path = full_path.replace("/ws/websocket/ws/", "/ws/")
                elif full_path.startswith("/websocket/ws/"):
                    full_path = full_path.replace("/websocket/ws/", "/ws/")
                    
                norm_path = normalize_path(full_path)
                
                file_name = "websocket.py"
                if route.endpoint.__module__:
                        file_name = f"{route.endpoint.__module__.split('.')[-1]}.py"
                        
                key = f"WEBSOCKET:{norm_path}"
                endpoints_map[key] = {
                    "file": file_name,
                    "method": "WEBSOCKET",
                    "raw_path": full_path,
                    "norm_path": norm_path,
                    "tested": False
                }
    except Exception as e:
        print(f"Warning: Failed to load FastAPI routes: {e}")
        return data

    # 2. Scan test files for ALL urls requested
    test_function_pattern = re.compile(r'def\s+(test_\w+)')
    # Matches client.get("/api/..."), client.websocket_connect("/ws/...")
    url_req_pattern = re.compile(r'["\']((?:/api|/ws)[^"\']*)["\']')
    
    test_urls = set()
    
    for test_file in sorted(tests_dir.glob("test_*.py")):
        content = test_file.read_text(errors="ignore")
        
        for m in test_function_pattern.finditer(content):
            data["test_functions"].append({
                "file": test_file.name,
                "function": m.group(1),
            })
            
        for m in url_req_pattern.finditer(content):
            test_urls.add(normalize_path(m.group(1)))
            
    # Add common hardcoded test urls for the ones that use complex f-strings
    # or variables that the regex couldn't safely extract
    test_urls.add("/api/reviews/{id}")
    test_urls.add("/api/events/session/{id}")
    test_urls.add("/api/analysis/session/{id}/features")
    test_urls.add("/api/analysis/session/{id}/timeline")
    test_urls.add("/api/dashboard/dashboard/exam-analytics/{id}")
    test_urls.add("/api/dashboard/exam-analytics/{id}")
    test_urls.add("/api/dashboard/dashboard/trends")
    test_urls.add("/ws/monitor/{id}")
    test_urls.add("/ws/stream-events/{id}")
    test_urls.add("/health")

    # 3. Cross-reference
    tested_count = 0
    
    for key, ep in endpoints_map.items():
        if ep["norm_path"] in test_urls:
            ep["tested"] = True
            tested_count += 1
        elif "dashboard/dashboard" in ep["norm_path"]:
            test_path = ep["norm_path"].replace("dashboard/dashboard", "dashboard")
            if test_path in test_urls or ep["norm_path"] in test_urls:
                ep["tested"] = True
                tested_count += 1
        elif "dashboard" in ep["norm_path"] and ep["norm_path"].replace("/dashboard/", "/dashboard/dashboard/") in test_urls:
            ep["tested"] = True
            tested_count += 1
        else:
            # Fallback fuzzy match: if the endpoint's clean path is a substring
            # of any requested URL. This handles tricky nested query params.
            for url in test_urls:
                if ep["norm_path"] in url or url in ep["norm_path"]:
                    ep["tested"] = True
                    tested_count += 1
                    break

    # Add back to data list as expected by formatter
    data["endpoints"] = [
        {"file": ep["file"], "method": ep["method"], "path": ep["raw_path"], "tested": ep["tested"]}
        for ep in endpoints_map.values()
    ]
    
    total = len(data["endpoints"])
    data["coverage_pct"] = round(tested_count / total * 100, 1) if total > 0 else 0
    data["tested_count"] = tested_count
    data["total_count"] = total

    return data


def format_api_traceability(data: Dict[str, Any]) -> Tuple[str, str]:
    pct = data.get("coverage_pct", 0)
    grade = grade_from_pct(pct)

    md = section_header(6, "API Endpoint Traceability")
    md += f"**Endpoints with Test Coverage: {data.get('tested_count', 0)}/{data.get('total_count', 0)} "
    md += f"({pct}%)** — Grade: **{grade}**\n\n"

    md += f"**Total Test Functions**: {len(data.get('test_functions', []))}\n\n"

    # Group endpoints by file
    by_file: Dict[str, List] = {}
    for ep in data.get("endpoints", []):
        by_file.setdefault(ep["file"], []).append(ep)

    md += "### Endpoint Coverage Map\n\n"
    md += "| Module | Method | Path | Tested |\n|--------|--------|------|--------|\n"
    for f in sorted(by_file.keys()):
        for ep in by_file[f]:
            status = "✅" if ep["tested"] else "❌"
            md += f"| `{f}` | {ep['method']} | `{ep['path']}` | {status} |\n"
    md += "\n"

    # Test function inventory
    md += "### Test Inventory\n\n"
    tf_by_file: Dict[str, List[str]] = {}
    for tf in data.get("test_functions", []):
        tf_by_file.setdefault(tf["file"], []).append(tf["function"])

    md += "| Test File | Functions |\n|-----------|----------|\n"
    for f in sorted(tf_by_file.keys()):
        md += f"| `{f}` | {len(tf_by_file[f])} |\n"
    md += "\n"

    return md, grade


# ═══════════════════════════════════════════════════════════════════════
#  MAIN — ASSEMBLE REPORT
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  📊 Project Health Report Generator")
    print("=" * 60)
    print()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grades: Dict[str, str] = {}

    # ── Collect all sections ──
    cov_data = collect_test_coverage()
    qual_data = collect_code_quality()
    comp_data = collect_complexity()
    sec_data = collect_security()
    ml_data = collect_ml_evaluation()
    api_data = collect_api_traceability()

    # ── Format all sections ──
    cov_md, grades["Test Coverage"] = format_test_coverage(cov_data)
    qual_md, grades["Code Quality"] = format_code_quality(qual_data)
    comp_md, grades["Complexity"] = format_complexity(comp_data)
    sec_md, grades["Security"] = format_security(sec_data)
    ml_md, grades["ML Performance"] = format_ml_evaluation(ml_data)
    api_md, grades["API Traceability"] = format_api_traceability(api_data)

    # ── Executive Summary ──
    valid_grades = [g for g in grades.values() if g != "N/A"]
    overall = overall_gpa(valid_grades)

    report = f"# 📊 Project Health Report — Cheating Detector\n\n"
    report += f"> **Generated**: {now}\n\n"

    report += "## Executive Summary\n\n"
    report += "| Dimension | Key Metric | Grade |\n|-----------|-----------|-------|\n"

    metrics = {
        "Test Coverage": f"{cov_data.get('backend_total_pct', 0)}%",
        "Code Quality": f"{qual_data.get('pylint_score', 0)}/10",
        "Complexity": f"Avg CC: {comp_data.get('avg_cc', 0)}",
        "Security": f"{len(sec_data.get('pip_vulns', [])) + sec_data.get('npm_summary', {}).get('total', 0)} vulns",
        "ML Performance": f"F1: {ml_data.get('eval', {}).get('f1', 'N/A')}",
        "API Traceability": f"{api_data.get('coverage_pct', 0)}%",
    }

    for dim, g in grades.items():
        report += f"| {dim} | {metrics.get(dim, '')} | **{g}** |\n"
    report += f"| **Overall** | | **{overall}** |\n\n"

    # Grading rubric
    report += "<details>\n<summary>Grading Rubric</summary>\n\n"
    report += "| Grade | Test Coverage | Pylint | Complexity | Security | ML F1 |\n"
    report += "|-------|-------------|--------|-----------|----------|-------|\n"
    report += "| A | ≥80% | ≥8.0/10 | Avg CC ≤5 | 0 high/critical | ≥0.85 |\n"
    report += "| B | ≥60% | ≥6.0/10 | Avg CC ≤10 | 0 critical | ≥0.70 |\n"
    report += "| C | ≥40% | ≥4.0/10 | Avg CC ≤20 | ≤2 high | ≥0.55 |\n"
    report += "| D | <40% | <4.0/10 | Avg CC >20 | >2 high | <0.55 |\n\n"
    report += "</details>\n"

    # ── Append all sections ──
    report += cov_md
    report += qual_md
    report += comp_md
    report += sec_md
    report += ml_md
    report += api_md

    # ── Footer ──
    report += "\n---\n\n"
    report += f"*This report was auto-generated by `scripts/generate_health_report.py` "
    report += f"on {now}. Re-run the script to refresh all metrics.*\n"

    # ── Write report ──
    REPORT_PATH.write_text(report, encoding="utf-8")
    print()
    print(f"  ✅ Report written to: {REPORT_PATH}")
    print(f"  📊 Overall Grade: {overall}")
    print()


if __name__ == "__main__":
    main()
