"""
core.search_indexer - Normalized In-Memory Text Search Indexer.
Pre-indexes record fields for high-speed sub-millisecond table filtering.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class IndexedRecord:
    record: Dict[str, Any]
    id_str: str
    normalized_name: str
    normalized_desc: str
    full_searchable: str

class SearchIndexer:
    def __init__(self):
        self.indexed_records: List[IndexedRecord] = []
        self._record_map: Dict[Any, IndexedRecord] = {}

    def clear(self):
        """Clears all indexed records."""
        self.indexed_records.clear()
        self._record_map.clear()

    def build_index(self, records: List[Dict[str, Any]], mode: str = "kernel"):
        """Pre-computes lowercase searchable text for all records in memory."""
        self.indexed_records.clear()
        self._record_map.clear()
        
        for r in records:
            eid = r.get('id', '')
            id_str = str(eid).lower()
            name = str(r.get('name', ''))
            desc = str(r.get('desc', ''))
            
            norm_name = name.replace('\r\n', ' ').replace('\n', ' ').lower()
            norm_desc = desc.replace('\r\n', ' ').replace('\n', ' ').lower()
            
            parts = [id_str, norm_name, norm_desc]
            for extra in ('sname', 'sdesc', 'w_wakka', 'w_lulu', 'w_rikku'):
                v = r.get(extra)
                if v and isinstance(v, str):
                    parts.append(v.replace('\r\n', ' ').replace('\n', ' ').lower())
            
            rec_entry = IndexedRecord(
                record=r,
                id_str=id_str,
                normalized_name=norm_name,
                normalized_desc=norm_desc,
                full_searchable=" | ".join(parts)
            )
            self.indexed_records.append(rec_entry)
            self._record_map[eid] = rec_entry

    def index_records(self, records: List[Dict[str, Any]], mode: str = "kernel"):
        """Alias for build_index."""
        self.build_index(records, mode)

    def filter(self, query: str, is_regex: bool = False, match_case: bool = False) -> List[Dict[str, Any]]:
        """Filters indexed records matching the query string."""
        if not query:
            return [ir.record for ir in self.indexed_records]
            
        q = query if match_case else query.lower()
        results = []
        
        if is_regex:
            flags = 0 if match_case else re.IGNORECASE
            try:
                pattern = re.compile(query, flags)
                for ir in self.indexed_records:
                    if pattern.search(ir.full_searchable):
                        results.append(ir.record)
                return results
            except Exception:
                return []
        else:
            for ir in self.indexed_records:
                target = ir.full_searchable if not match_case else (
                    f"{ir.record.get('id')} | {ir.record.get('name', '')} | {ir.record.get('desc', '')}"
                )
                if q in target:
                    results.append(ir.record)
            return results

    def search(self, query: str, is_regex: bool = False, match_case: bool = False) -> List[Dict[str, Any]]:
        """Alias for filter."""
        return self.filter(query, is_regex=is_regex, match_case=match_case)
