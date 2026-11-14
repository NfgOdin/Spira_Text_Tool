import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core import (
    FFXCodec, QAEngine, QAError, estimate_vo_duration, auto_fix_string,
    BatchRulesEngine, BatchRule, apply_rules_to_string,
    SearchIndexer, create_mod_archive, encode_spiramod_meta, decode_spiramod_meta,
    CANONICAL_LORE_GLOSSARY, lookup_lore_term, index_lore_terms,
    TaskWorker, TaskProgress
)

class TestCoreEngines(unittest.TestCase):
    def test_01_codec_and_unsupported_characters(self):
        codec = FFXCodec()
        loaded = codec.load_charset("us")
        self.assertTrue(loaded, "Failed to load 'us' charset")

        # Standard ASCII characters should have 0 unsupported characters
        unsupported = codec.get_unsupported_characters("Hello Spira! {CLR:YELLOW}Overdrive{CLR:WHITE}", "us")
        self.assertEqual(unsupported, [])

        # Non-US character (e.g., Cyrillic 'Д' or emoji) should be detected as unsupported in 'us' charset
        unsupported = codec.get_unsupported_characters("Potion Д 🛡️", "us")
        self.assertIn("Д", unsupported)
        self.assertIn("🛡", unsupported)

    def test_02_canonical_lore(self):
        self.assertGreaterEqual(len(CANONICAL_LORE_GLOSSARY), 100)
        
        # Test lookup
        term = lookup_lore_term("Tidus", "en")
        self.assertIsNotNone(term)
        self.assertEqual(term["jp"], "ティーダ")
        
        # Test lookup across non-en
        term_jp = lookup_lore_term("ユウナ")
        self.assertIsNotNone(term_jp)
        self.assertEqual(term_jp["en"], "Yuna")

        # Test indexer
        indexed = index_lore_terms("en", "jp")
        self.assertIn("Auron", indexed)
        self.assertEqual(indexed["Auron"], "アーロン")

    def test_03_qa_engine_and_vo_estimator(self):
        codec = FFXCodec()
        codec.load_charset("us")
        qa = QAEngine(codec)

        # 1. Bracket imbalance
        issues = qa.audit_record_field("Broken {CLR:YELLOW text", "name", 1, "test.bin")
        self.assertTrue(any("Unbalanced braces" in i.message for i in issues))

        # 2. Tag whitespace
        issues = qa.audit_record_field("Hello { CLR:YELLOW }", "name", 2, "test.bin")
        self.assertTrue(any("Whitespace inside tag" in i.message for i in issues))

        # 3. Line overflow (>50 chars)
        issues = qa.audit_record_field("A" * 55, "name", 3, "test.bin")
        self.assertTrue(any("overflow" in i.message.lower() for i in issues))

        # 4. Unclosed color
        issues = qa.audit_record_field("{CLR:YELLOW}Leaking Yellow", "name", 4, "test.bin")
        self.assertTrue(any("Unclosed color tag" in i.message for i in issues))

        # 5. Safe auto-fix
        fixed = auto_fix_string("{CLR:YELLOW}Text", "append_white")
        self.assertEqual(fixed, "{CLR:YELLOW}Text{CLR:WHITE}")

        fixed_ws = auto_fix_string("{ CLR:YELLOW }", "normalize_tag_whitespace")
        self.assertEqual(fixed_ws, "{CLR:YELLOW}")

        fixed_trim = auto_fix_string("Line 1   \nLine 2 \t", "trim_trailing_whitespace")
        self.assertEqual(fixed_trim, "Line 1\nLine 2")

        # 6. VO Estimator
        # 60 frames (0x3C) at 30fps = 2.0 seconds
        dur, cps, wpm = estimate_vo_duration("{TIME:3C}Tidus speaks for two seconds right now.")
        self.assertEqual(dur, 2.0)
        self.assertGreater(cps, 10.0)
        self.assertGreater(wpm, 100.0)

    def test_04_rules_engine(self):
        rules = [
            BatchRule(find="Potion", replace="Elixir", match_case=True, regex=False),
            BatchRule(find=r"HP\+(\d+)", replace=r"Health+\1", match_case=True, regex=True)
        ]
        
        text = "Use Potion to gain HP+500!"
        out, count = apply_rules_to_string(text, rules)
        self.assertEqual(out, "Use Elixir to gain Health+500!")
        self.assertEqual(count, 2)

        # Save and reload
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            tf_path = tf.name
        try:
            ok = BatchRulesEngine.save_ruleset(tf_path, rules, "TestRules")
            self.assertTrue(ok)
            loaded_rules = BatchRulesEngine.load_ruleset(tf_path)
            self.assertEqual(len(loaded_rules), 2)
            self.assertEqual(loaded_rules[0].find, "Potion")
            self.assertEqual(loaded_rules[1].replace, r"Health+\1")
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    def test_05_search_indexer(self):
        indexer = SearchIndexer()
        records = [
            {'id': 0, 'name': 'Potion', 'desc': 'Restores 200 HP.'},
            {'id': 1, 'name': 'Hi-Potion', 'desc': 'Restores 1000 HP.'},
            {'id': 2, 'name': 'Phoenix Down', 'desc': 'Revives fallen ally.'}
        ]
        indexer.build_index(records)

        # Plain search
        res = indexer.filter("potion")
        self.assertEqual(len(res), 2)

        # Unique search term
        res_unique = indexer.filter("Phoenix")
        self.assertEqual(len(res_unique), 1)
        self.assertEqual(res_unique[0]['name'], 'Phoenix Down')

        # Regex search
        res_rgx = indexer.filter(r"HP\.$", is_regex=True)
        self.assertEqual(len(res_rgx), 2)

    def test_06_mod_packaging(self):
        meta = {"name": "TestMod", "author": "Tester", "version": "1.0.0"}
        encoded = encode_spiramod_meta(meta)
        self.assertTrue(len(encoded) > 10)
        decoded = decode_spiramod_meta(encoded)
        self.assertEqual(decoded["name"], "TestMod")

        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
            tf.write(b"SAMPLE_BIN_DATA")
            dummy_bin = tf.name
            
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tf_zip:
            out_zip = tf_zip.name

        try:
            ok, count, size_kb, msg = create_mod_archive(
                out_path=out_zip,
                files_to_pack=[(dummy_bin, "ffx_ps2/ffx/master/new_uspc/item_txt.bin")],
                name="Test Package",
                author="Odin"
            )
            self.assertTrue(ok)
            self.assertEqual(count, 1)
            self.assertGreater(size_kb, 0.0)
            self.assertTrue(os.path.exists(out_zip))
        finally:
            if os.path.exists(dummy_bin):
                os.remove(dummy_bin)
            if os.path.exists(out_zip):
                os.remove(out_zip)

    def test_07_task_worker(self):
        import time

        def dummy_heavy_task(worker: TaskWorker):
            total = 5
            for i in range(1, total + 1):
                if worker.is_cancelled():
                    return "Cancelled"
                worker.post_progress(i, total, f"Step {i}")
                time.sleep(0.01)
            return "Done"

        worker = TaskWorker(dummy_heavy_task, "TestWorker")
        worker.start()

        stages = []
        start_t = time.time()
        while time.time() - start_t < 2.0:
            try:
                prog = worker.queue.get(timeout=0.2)
                stages.append(prog.stage)
                if prog.stage in ("complete", "error", "cancelled"):
                    break
            except Exception:
                pass

        self.assertIn("running", stages)
        self.assertIn("complete", stages)

if __name__ == "__main__":
    unittest.main()
