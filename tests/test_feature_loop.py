"""Offline checks for the loop's structural sensor and deterministic decision signal."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from scripts.feature_loop import analyze, decision


class LoopContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.feature = self.root / 'specs' / 'transcript-extraction'
        self.feature.mkdir(parents=True)
        (self.feature / 'spec.md').write_text('**FR-001** **SC-001**', encoding='utf-8')

    def test_missing_plan_and_tasks_never_claims_ready(self):
        report = analyze(self.root)
        self.assertTrue(any('NOT_READY' in x for x in report['findings']))
        self.assertEqual('PLAN_OR_RECONCILE', decision({'structural': report, 'checks': []})['action'])

    def test_spec_tasks_traceability_and_one_task_selection(self):
        (self.feature / 'plan.md').write_text('# Design\n', encoding='utf-8')
        (self.feature / 'tasks.md').write_text('- [x] T001 FR-001 done\n- [ ] T002 SC-001 verify\n', encoding='utf-8')
        report = analyze(self.root)
        self.assertFalse(report['findings'])
        self.assertEqual(1, report['task_done'])
        self.assertEqual('T002', decision({'structural': report, 'checks': [], 'checks_executed': True})['task']['id'])

    def test_duplicate_tasks_block(self):
        (self.feature / 'plan.md').write_text('# Plan', encoding='utf-8')
        (self.feature / 'tasks.md').write_text('- [ ] T001 FR-001\n- [ ] T001 SC-001', encoding='utf-8')
        report = analyze(self.root)
        self.assertEqual('BLOCKED', decision({'structural': report, 'checks': []})['action'])

    def test_failed_regression_preempts_next_task(self):
        (self.feature / 'plan.md').write_text('# Plan', encoding='utf-8')
        (self.feature / 'tasks.md').write_text('- [ ] T001 FR-001 SC-001', encoding='utf-8')
        report = analyze(self.root)
        self.assertEqual('DIAGNOSE', decision({'structural': report, 'checks': [{'check': 'regression', 'status': 'FAIL'}]})['action'])

    def test_baseline_is_required_before_implementation(self):
        (self.feature / 'plan.md').write_text('# Plan', encoding='utf-8')
        (self.feature / 'tasks.md').write_text('- [ ] T001 FR-001 SC-001', encoding='utf-8')
        report = analyze(self.root)
        self.assertEqual('RUN_BASELINE', decision({'structural': report, 'checks': [], 'checks_executed': False})['action'])

    def test_unmapped_requirements_prevent_execution(self):
        (self.feature / 'plan.md').write_text('# Plan', encoding='utf-8')
        (self.feature / 'tasks.md').write_text('- [ ] T001 FR-001', encoding='utf-8')
        report = analyze(self.root)
        self.assertEqual(['SC-001'], report['unmapped_requirement_ids'])
        self.assertEqual('PLAN_OR_RECONCILE', decision({'structural': report, 'checks': []})['action'])


if __name__ == '__main__':
    unittest.main()
