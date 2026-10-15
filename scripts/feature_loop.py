#!/usr/bin/env python3
"""Deterministic read/measure/select aid for the VD-02 Codex control loop.

Not an autonomous runner and not an acceptance certificate. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = Path('specs/transcript-extraction/spec.md')
PLAN_PATH = Path('specs/transcript-extraction/plan.md')
TASKS_PATH = Path('specs/transcript-extraction/tasks.md')
ID_PATTERN = re.compile(r'\b(?:FR|SC)-\d{3}\b')
TASK_PATTERN = re.compile(r'^\s*- \[([ xX])\] (T\d{3,})\b(.*)$', re.MULTILINE)


def analyze(root: Path) -> dict:
    """Inspect source-of-truth artifacts; no guesses from checked boxes."""
    spec = root / SPEC_PATH
    plan = root / PLAN_PATH
    tasks = root / TASKS_PATH
    findings = []
    spec_text = spec.read_text(encoding='utf-8') if spec.is_file() else ''
    tasks_text = tasks.read_text(encoding='utf-8') if tasks.is_file() else ''
    if not spec_text:
        findings.append('BLOCKED: feature specification missing or empty')
    ids = sorted(set(ID_PATTERN.findall(spec_text)))
    if not ids:
        findings.append('BLOCKED: no FR-/SC- requirement identifiers found')
    if not plan.is_file() or not plan.read_text(encoding='utf-8').strip():
        findings.append('NOT_READY: plan.md missing or empty (Spec Kit planning required)')
    if not tasks_text:
        findings.append('NOT_READY: tasks.md missing or empty (Spec Kit tasks required)')
    task_matches = list(TASK_PATTERN.finditer(tasks_text))
    task_list = [{'id': m.group(2), 'done': m.group(1).lower() == 'x', 'description': m.group(3).strip()}
                 for m in task_matches]
    if tasks_text and not task_list:
        findings.append('BLOCKED: no Spec Kit T### checklist tasks parsed')
    task_ids = [t['id'] for t in task_list]
    if len(task_ids) != len(set(task_ids)):
        findings.append('BLOCKED: duplicate task identifiers')
    # Explicit references are only structural traceability, not proof of test quality.
    task_coverage = sorted(id_ for id_ in ids if id_ not in tasks_text)
    if tasks_text and task_coverage:
        findings.append('NOT_READY: requirement IDs not explicitly mapped in tasks.md')
    return {
        'spec_ids': ids,
        'task_count': len(task_list),
        'task_done': sum(t['done'] for t in task_list),
        'unmapped_requirement_ids': task_coverage,
        'next_unchecked_task': next((t for t in task_list if not t['done']), None),
        'findings': findings,
        'scope': 'Structural traceability only; no claim about product behavior, test coverage, UI or installer',
    }


def run_checks(root: Path, *, timeout: int) -> list[dict]:
    """Execute only the repository's fixed local checks, without shell/network."""
    commands = [
        ('syntax', [sys.executable, '-m', 'compileall', '-q', 'app', 'scripts/feature_loop.py']),
        ('regression', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
    ]
    reports = []
    for name, args in commands:
        try:
            p = subprocess.run(args, cwd=root, text=True, capture_output=True,
                               timeout=timeout, check=False, encoding='utf-8', errors='replace')
            output = p.stdout + '\n' + p.stderr
            skipped = re.search(r'\bskipped=(\d+)\b', output)
            reports.append({'check': name, 'command': args, 'exit_code': p.returncode,
                            'status': ('PASS_WITH_SKIPS' if skipped and int(skipped.group(1)) else 'PASS') if p.returncode == 0 else 'FAIL',
                            'skipped_tests': int(skipped.group(1)) if skipped else 0,
                            'output_tail': output[-4500:]})
        except subprocess.TimeoutExpired:
            reports.append({'check': name, 'command': args, 'status': 'BLOCKED',
                            'reason': f'Timed out after {timeout}s'})
        except OSError as exc:
            reports.append({'check': name, 'command': args, 'status': 'BLOCKED',
                            'reason': f'{type(exc).__name__}: {exc}'})
    return reports


def decision(measurement: dict) -> dict:
    """Deterministic controller signal. Codex retains bounded change judgment."""
    failed = [v['check'] for v in measurement.get('checks', []) if v['status'] in ('FAIL', 'BLOCKED')]
    if failed:
        return {'action': 'DIAGNOSE', 'targets': failed,
                'reason': 'Do not advance feature implementation while relevant existing checks fail'}
    findings = measurement['structural']['findings']
    if any(s.startswith('BLOCKED') for s in findings):
        return {'action': 'BLOCKED', 'reason': '; '.join(s for s in findings if s.startswith('BLOCKED'))}
    if findings:
        return {'action': 'PLAN_OR_RECONCILE', 'reason': '; '.join(findings)}
    if not measurement.get('checks_executed', False):
        return {'action': 'RUN_BASELINE', 'reason': 'Baseline checks were not executed; use next --run-checks'}
    task = measurement['structural']['next_unchecked_task']
    if task:
        return {'action': 'IMPLEMENT_ONE', 'task': task,
                'reason': 'Spec Kit task order; agent must verify real dependencies and acceptance before edits'}
    return {'action': 'VERIFY_RELEASE', 'reason': 'All task boxes checked; independently verify each FR/SC, full archive, UI, installer and review evidence'}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('measure', 'next'))
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--run-checks', action='store_true', help='Run compileall and unittest, no network smoke flags set')
    ap.add_argument('--timeout', type=int, default=180)
    ns = ap.parse_args(argv)
    if ns.timeout < 1 or ns.timeout > 3600:
        ap.error('--timeout must be from 1 to 3600 seconds')
    root = ns.root.resolve()
    structural = analyze(root)
    measurement = {'root': str(root), 'python': sys.executable, 'structural': structural,
                   'checks': run_checks(root, timeout=ns.timeout) if ns.run_checks else [],
                   'checks_executed': bool(ns.run_checks)}
    if ns.mode == 'next':
        measurement['controller'] = decision(measurement)
    print(json.dumps(measurement, ensure_ascii=True, indent=2))
    if any(c.get('status') in ('FAIL', 'BLOCKED') for c in measurement['checks']):
        return 1
    return 2 if any(s.startswith('BLOCKED') for s in structural['findings']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
