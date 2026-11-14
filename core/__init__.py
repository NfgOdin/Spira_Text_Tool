"""
core - Headless Engine & Business Logic Subsystem for FFX & FFX-2 Localization Studio.
"""

from .codec import FFXCodec, COLOR_MAP, COLOR_REV, FILE_RECORD_SIZES
from .qa_engine import QAEngine, QAError, estimate_vo_duration, auto_fix_string
from .rules_engine import BatchRulesEngine, BatchRule, apply_rules_to_string
from .search_indexer import SearchIndexer, IndexedRecord
from .mod_packaging import create_mod_archive, encode_spiramod_meta, decode_spiramod_meta
from .lore_db import CANONICAL_LORE_GLOSSARY, get_all_lore_terms, lookup_lore_term, index_lore_terms
from .task_worker import TaskWorker, TaskProgress

__all__ = [
    "FFXCodec",
    "COLOR_MAP",
    "COLOR_REV",
    "FILE_RECORD_SIZES",
    "QAEngine",
    "QAError",
    "estimate_vo_duration",
    "auto_fix_string",
    "BatchRulesEngine",
    "BatchRule",
    "apply_rules_to_string",
    "SearchIndexer",
    "IndexedRecord",
    "create_mod_archive",
    "encode_spiramod_meta",
    "decode_spiramod_meta",
    "CANONICAL_LORE_GLOSSARY",
    "get_all_lore_terms",
    "lookup_lore_term",
    "index_lore_terms",
    "TaskWorker",
    "TaskProgress",
]
