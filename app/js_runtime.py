"""Resolve existing local JavaScript runtimes without downloading components."""
from __future__ import annotations

import shutil

from app.paths import resource_path


def resolve_js_runtimes() -> dict:
    for name, executable in (('deno', 'deno'), ('node', 'node')):
        for suffix in ('.exe', ''):
            bundled = resource_path(f'tools/javascript/{executable}{suffix}')
            if bundled.is_file():
                return {name: {'path': str(bundled)}}
    for name in ('deno', 'node'):
        path = shutil.which(name)
        if path:
            return {name: {'path': path}}
    return {}
