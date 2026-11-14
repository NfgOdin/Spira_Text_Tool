"""
core.qa_engine - Automated QA Syntax, In-Game Crash Prevention & VO Estimator.
Performs headless deep validation for:
- Bracket balance ({ vs })
- Unknown / malformed engine tags
- Unclosed color tags ({CLR:...} leaking into subsequent text)
- Dialogue width overflow (>43 chars safe limit, >50 chars cutoff)
- Dialogue line height overflow (>4 lines)
- Entry byte capacity (>500B warning, >800B capacity limit)
- 16-bit offset pool overflow (>60,000B warning, >65,535B FATAL pointer crash)
- Cutscene Voice-Over (VO) speech rate estimation (CPS / WPM)
"""

import os
import re
import shutil
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

KNOWN_TAG_PREFIXES = (
    "CLR:", "TIME:", "WAIT:", "KEY:", "CHOICE:", "CHOICE-END", "VAR:", "VO_VAR:",
    "NUM:", "NAME:", "MACRO:", "MCR:", "CHAR:", "ITEM:", "MAP:", "SPACE:",
    "PAD_", "BTN_", "PC:", "CTRL:", "CMD:", "UNKP:", "UNK:", "PAUSE", "NEWLINE"
)

@dataclass
class QAError:
    severity: str        # 'CRITICAL', 'WARNING', 'INFO'
    file: str
    entry_id: Any
    field: str
    message: str
    snippet: str
    is_fixable: bool
    fix_type: Optional[str]
    file_path: str

    @property
    def file_name(self) -> str:
        return self.file

    @property
    def is_auto_fixable(self) -> bool:
        return self.is_fixable

    def to_tuple(self):
        sev_display = f"🔴 {self.severity}" if self.severity == "CRITICAL" else f"🟡 {self.severity}"
        return (sev_display, self.file, self.entry_id, self.field, self.message, self.snippet, self.is_fixable, self.fix_type, self.file_path)

def estimate_vo_duration(text: str, default_fps: float = 30.0) -> Tuple[float, float, float]:
    """
    Calculates estimated cutscene display duration and speech rate metrics.
    Returns: (duration_seconds, characters_per_second, words_per_minute)
    """
    if not text:
        return (0.0, 0.0, 0.0)

    # 1. Check for explicit {TIME:XX} tags (hex frames, e.g. {TIME:1E} = 30 frames = 1.0s)
    time_tags = re.findall(r'\{TIME:([0-9A-Fa-f]+)\}', text)
    total_frames = 0
    for h in time_tags:
        try:
            total_frames += int(h, 16)
        except ValueError:
            pass

    # Clean text (remove tags)
    clean_text = re.sub(r'\{[^}]+\}', '', text).strip()
    char_count = len(clean_text)
    word_count = len(clean_text.split())

    if total_frames > 0:
        duration_sec = total_frames / default_fps
    else:
        # Default speaking rate ~14-16 chars/sec (~150 WPM)
        duration_sec = max(1.0, char_count / 15.0)

    cps = char_count / duration_sec if duration_sec > 0 else 0.0
    wpm = (word_count / (duration_sec / 60.0)) if duration_sec > 0 else 0.0

    return (round(duration_sec, 2), round(cps, 1), round(wpm, 1))

def auto_fix_string(text: str, fix_type: str) -> str:
    """Applies safe automatic formatting repair to a string."""
    if not text or not isinstance(text, str):
        return text

    new_s = text
    if fix_type == 'append_white':
        if not new_s.endswith("{CLR:WHITE}"):
            new_s = new_s + "{CLR:WHITE}"
    elif fix_type == 'normalize_tag_whitespace':
        new_s = re.sub(r'\{\s*([A-Za-z0-9_]+)\s*(?::\s*([^}]+?)\s*)?\}',
                       lambda m: f"{{{m.group(1)}:{m.group(2).strip()}}}" if m.group(2) else f"{{{m.group(1)}}}", new_s)
    elif fix_type in ('trim_trailing_whitespace', 'trailing_space'):
        new_s = '\n'.join(line.rstrip() for line in new_s.split('\n')).rstrip()
    elif fix_type == 'unclosed_tag':
        if new_s.count("{") > new_s.count("}"):
            new_s = new_s + "}" * (new_s.count("{") - new_s.count("}"))

    return new_s

class QAEngine:
    def __init__(self, codec=None):
        self.codec = codec

    def audit_record_field(self, val: str, field_name: str, entry_id: Any, file_label: str, file_path: str = "", charset: str = "us") -> List[QAError]:
        """Audits a single string field."""
        issues: List[QAError] = []
        if not val or not isinstance(val, str):
            return issues

        # 1. Bracket balance
        n_open = val.count('{')
        n_close = val.count('}')
        if n_open != n_close:
            issues.append(QAError(
                severity='CRITICAL',
                file=file_label,
                entry_id=entry_id,
                field=field_name,
                message=f"Unbalanced braces: {n_open} '{{' vs {n_close} '}}'",
                snippet=val[:60],
                is_fixable=False,
                fix_type=None,
                file_path=file_path
            ))

        # 2. Tag format & whitespace
        tags = re.findall(r'\{([^}]+)\}', val)
        for t in tags:
            ct = t.strip()
            if ' ' in t:
                issues.append(QAError(
                    severity='WARNING',
                    file=file_label,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Whitespace inside tag: '{{{t}}}'",
                    snippet=f"{{{t}}}",
                    is_fixable=True,
                    fix_type='normalize_tag_whitespace',
                    file_path=file_path
                ))
            if not any(ct.upper().startswith(k) or ct.upper() == k for k in KNOWN_TAG_PREFIXES):
                issues.append(QAError(
                    severity='WARNING',
                    file=file_label,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Unrecognized engine tag: '{{{t}}}'",
                    snippet=f"{{{t}}}",
                    is_fixable=False,
                    fix_type=None,
                    file_path=file_path
                ))

        # 3. Line width and height analysis
        lines = val.replace("{\\n}", "\n").replace("{/n}", "\n").replace("{n}", "\n").split('\n')
        if any(l.endswith(' ') or l.endswith('\t') for l in lines):
            issues.append(QAError(
                severity='WARNING',
                file=file_label,
                entry_id=entry_id,
                field=field_name,
                message="Trailing whitespace detected on line(s)",
                snippet=val[:40],
                is_fixable=True,
                fix_type='trim_trailing_whitespace',
                file_path=file_path
            ))

        clean_lines = [re.sub(r'\{[^}]+\}', '', l) for l in lines]
        for l_idx, cl in enumerate(clean_lines, 1):
            if len(cl) > 50:
                issues.append(QAError(
                    severity='CRITICAL',
                    file=file_label,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Line {l_idx} overflow: {len(cl)} chars (>50 chars, cutoff imminent)",
                    snippet=cl[:45] + "...",
                    is_fixable=False,
                    fix_type=None,
                    file_path=file_path
                ))
            elif len(cl) > 43:
                issues.append(QAError(
                    severity='WARNING',
                    file=file_label,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Line {l_idx} width: {len(cl)} chars (safe width ~42-43 chars)",
                    snippet=cl[:45] + "...",
                    is_fixable=False,
                    fix_type=None,
                    file_path=file_path
                ))

        if len(clean_lines) > 4:
            issues.append(QAError(
                severity='WARNING',
                file=file_label,
                entry_id=entry_id,
                field=field_name,
                message=f"Height overflow: {len(clean_lines)} lines (box displays max 4 lines)",
                snippet=clean_lines[0][:40],
                is_fixable=False,
                fix_type=None,
                file_path=file_path
            ))

        # 4. Color tag closure ({CLR:WHITE})
        clrs = re.findall(r'\{CLR:([^}]+)\}', val)
        if clrs:
            last_clr = clrs[-1].upper()
            if last_clr != "WHITE":
                issues.append(QAError(
                    severity='WARNING',
                    file=file_label,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Unclosed color tag (ends in '{last_clr}', will leak without {{CLR:WHITE}})",
                    snippet=val[-40:],
                    is_fixable=True,
                    fix_type='append_white',
                    file_path=file_path
                ))

        # 5. Entry byte capacity (if codec is provided)
        if self.codec:
            try:
                encoded_len = len(self.codec.encode_ffx_string(val, charset))
                if encoded_len > 800:
                    issues.append(QAError(
                        severity='CRITICAL',
                        file=file_label,
                        entry_id=entry_id,
                        field=field_name,
                        message=f"Entry size {encoded_len}B exceeds 800B capacity limit!",
                        snippet=val[:40],
                        is_fixable=False,
                        fix_type=None,
                        file_path=file_path
                    ))
                elif encoded_len > 500:
                    issues.append(QAError(
                        severity='WARNING',
                        file=file_label,
                        entry_id=entry_id,
                        field=field_name,
                        message=f"Entry size {encoded_len}B is high (>500B)",
                        snippet=val[:40],
                        is_fixable=False,
                        fix_type=None,
                        file_path=file_path
                    ))
            except Exception:
                pass

        return issues

    def audit_records_pool(self, records: List[Dict[str, Any]], file_label: str, file_path: str, charset: str = "us") -> List[QAError]:
        """Audits table pool size against the 16-bit offset limit (65,535 bytes)."""
        issues: List[QAError] = []
        if not records or not self.codec:
            return issues

        unique_strings = set()
        for r in records:
            for fld in ('name', 'sname', 'desc', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku'):
                v = r.get(fld)
                if v and isinstance(v, str):
                    unique_strings.add(v)

        try:
            pool_size = sum(len(self.codec.encode_ffx_string(s, charset)) + 1 for s in unique_strings)
            if pool_size > 65535:
                issues.append(QAError(
                    severity='CRITICAL',
                    file=file_label,
                    entry_id=0,
                    field='FILE_POOL',
                    message=f"FATAL POINTER OVERFLOW: Pool is {pool_size}B (>65,535B 16-bit limit)! WILL CRASH ENGINE",
                    snippet=f"{len(unique_strings)} strings",
                    is_fixable=False,
                    fix_type=None,
                    file_path=file_path
                ))
            elif pool_size > 60000:
                issues.append(QAError(
                    severity='WARNING',
                    file=file_label,
                    entry_id=0,
                    field='FILE_POOL',
                    message=f"Pool size {pool_size}B is dangerously close to 65,535B limit!",
                    snippet=f"{len(unique_strings)} strings",
                    is_fixable=False,
                    fix_type=None,
                    file_path=file_path
                ))
        except Exception:
            pass

        return issues

    def audit_record(self, record: Dict[str, Any], file_label: str, file_path: str, charset: str = "us") -> List[QAError]:
        """Audits all string fields of a single record."""
        issues: List[QAError] = []
        eid = record.get('id', 0)
        fields = [('name', record.get('name', ''))]
        for opt in ('sname', 'desc', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku'):
            if opt in record and record.get(opt):
                fields.append((opt, record.get(opt, '')))

        for fld, val in fields:
            issues.extend(self.audit_record_field(val, fld, eid, file_label, file_path, charset))
        return issues

    def audit_records(self, records: List[Dict[str, Any]], file_label: str, file_path: str = "", charset: str = "us") -> List[QAError]:
        """Audits a full list of records, including file-level pool overflow checks."""
        issues: List[QAError] = []
        for r in records:
            issues.extend(self.audit_record(r, file_label, file_path, charset))
        issues.extend(self.audit_records_pool(records, file_label, file_path, charset))
        return issues
