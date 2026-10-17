"""Remove credentials and provider URLs before messages reach logs or the UI."""
from __future__ import annotations

import logging
import re
import traceback
from urllib.parse import urlsplit

_URL = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
_HEADER = re.compile(r'\b(authorization|proxy-authorization|set-cookie|cookie)\s*[:=][^\r\n]*', re.IGNORECASE)
_SECRET = re.compile(r'\b(password|passwd|token|access_token|api[_-]?key|signature|sig)\s*[:=]\s*(?:"[^"]*"|\x27[^\x27]*\x27|[^\s,;]+)', re.IGNORECASE)


def redact(message: object) -> str:
    def domain(match):
        try:
            host = urlsplit(match[0]).hostname
        except ValueError:
            host = None
        return '[URL ' + (host or 'redacted') + ']'
    text = _URL.sub(domain, str(message))
    text = _HEADER.sub(lambda match: match[1] + ': [redacted]', text)
    return _SECRET.sub(lambda match: match[1] + '=[redacted]', text)


class PrivacyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        if record.exc_info:
            record.exc_text = redact(''.join(traceback.format_exception(*record.exc_info)))
            record.exc_info = None
        elif record.exc_text:
            record.exc_text = redact(record.exc_text)
        if record.stack_info:
            record.stack_info = redact(record.stack_info)
        return True
