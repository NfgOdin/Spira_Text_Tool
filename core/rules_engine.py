"""
core.rules_engine - Reusable Batch Replacement Ruleset Manager.
Supports ordered sequential text and regex replacement pipelines with JSON serialization.
"""

import os
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Any

@dataclass
class BatchRule:
    find: str
    replace: str
    match_case: bool = True
    regex: bool = False

def apply_rules_to_string(text: str, rules: List[Any]) -> Tuple[str, int]:
    """
    Applies a sequential series of find/replace rules to a string.
    Rules can be BatchRule objects or dicts with keys 'find', 'replace', 'match_case', 'regex'.
    """
    if not text or not isinstance(text, str):
        return (text, 0)

    out = text
    rep_count = 0
    for r in rules:
        if isinstance(r, dict):
            pat = r.get('find', '')
            repl = r.get('replace', '')
            mc = r.get('match_case', True)
            is_rgx = r.get('regex', False)
        else:
            pat = r.find
            repl = r.replace
            mc = r.match_case
            is_rgx = r.regex

        if not pat:
            continue

        if is_rgx:
            flags = 0 if mc else re.IGNORECASE
            try:
                out, n = re.subn(pat, repl, out, flags=flags)
                rep_count += n
            except Exception:
                pass
        else:
            if mc:
                n = out.count(pat)
                out = out.replace(pat, repl)
                rep_count += n
            else:
                pattern = re.compile(re.escape(pat), re.IGNORECASE)
                out, n = pattern.subn(repl, out)
                rep_count += n

    return out, rep_count

class BatchRulesEngine:
    @staticmethod
    def load_ruleset(filepath: str) -> List[BatchRule]:
        """Loads rules from a JSON ruleset file."""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rules = []
            items = data.get('rules', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            for item in items:
                rules.append(BatchRule(
                    find=item.get('find', ''),
                    replace=item.get('replace', ''),
                    match_case=item.get('match_case', True),
                    regex=item.get('regex', False)
                ))
            return rules
        except Exception:
            return []

    @staticmethod
    def save_ruleset(filepath_or_rules: Any, rules_or_filepath: Any, name: str = "Ruleset") -> bool:
        """Saves rules to a JSON ruleset file."""
        if isinstance(filepath_or_rules, (list, tuple)):
            rules = filepath_or_rules
            filepath = rules_or_filepath
        else:
            filepath = filepath_or_rules
            rules = rules_or_filepath

        try:
            payload = {
                "name": name,
                "version": "2.0.0",
                "rules": [asdict(r) if hasattr(r, '__dataclass_fields__') else dict(r) for r in rules]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def apply_to_record(record: Dict[str, Any], rules: List[Any], fields: Tuple[str, ...] = ('name', 'sname', 'desc', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku')) -> Tuple[Dict[str, Any], int]:
        """Applies batch rules across all target fields in a record."""
        total_reps = 0
        for fld in fields:
            val = record.get(fld)
            if val and isinstance(val, str):
                new_val, n = apply_rules_to_string(val, rules)
                if n > 0:
                    record[fld] = new_val
                    total_reps += n
        return record, total_reps

load_ruleset = BatchRulesEngine.load_ruleset
save_ruleset = BatchRulesEngine.save_ruleset
