import os
import sys
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from rss_storage import (  # noqa: E402
    LISBON_TZ,
    daily_data_path,
    existing_complete_by_link,
    has_complete_details,
    lisbon_today,
    load_json_list,
    merge_procedimentos_by_link,
)


class TestLisbonDate(unittest.TestCase):
    def test_lisbon_today_matches_timezone(self):
        expected = datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%d-%m-%Y")
        self.assertEqual(lisbon_today(), expected)

    def test_daily_data_path_uses_lisbon_date(self):
        path = daily_data_path("/tmp/data")
        self.assertEqual(path, f"/tmp/data/{lisbon_today()}.json")
        self.assertEqual(LISBON_TZ.key, "Europe/Lisbon")


class TestHasCompleteDetails(unittest.TestCase):
    def test_missing_or_empty(self):
        self.assertFalse(has_complete_details({}))
        self.assertFalse(has_complete_details({"detalhes_completos": ""}))
        self.assertFalse(has_complete_details({"detalhes_completos": "   "}))
        self.assertFalse(has_complete_details({"detalhes_completos": None}))

    def test_present(self):
        self.assertTrue(has_complete_details({"detalhes_completos": "NIPC: 1"}))


class TestMergeProcedimentos(unittest.TestCase):
    def test_keeps_morning_items_missing_from_later_rss(self):
        morning = [
            {
                "link": "https://dre.pt/a",
                "entidade": "A",
                "detalhes_completos": "detalhe A",
            }
        ]
        afternoon_rss = [
            {
                "link": "https://dre.pt/b",
                "entidade": "B",
                "detalhes_completos": "detalhe B",
            }
        ]
        merged = merge_procedimentos_by_link(morning, afternoon_rss)
        links = [item["link"] for item in merged]
        self.assertEqual(links, ["https://dre.pt/a", "https://dre.pt/b"])

    def test_does_not_overwrite_complete_record_with_rss_stub(self):
        existing = [
            {
                "link": "https://dre.pt/a",
                "entidade": "Completo",
                "detalhes_completos": "já extraído",
            }
        ]
        incoming = [{"link": "https://dre.pt/a", "entidade": "Só RSS"}]
        merged = merge_procedimentos_by_link(existing, incoming)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["entidade"], "Completo")
        self.assertEqual(merged[0]["detalhes_completos"], "já extraído")

    def test_upgrades_incomplete_record_when_details_arrive(self):
        existing = [{"link": "https://dre.pt/a", "entidade": "Incompleto"}]
        incoming = [
            {
                "link": "https://dre.pt/a",
                "entidade": "Completo",
                "detalhes_completos": "agora sim",
            }
        ]
        merged = merge_procedimentos_by_link(existing, incoming)
        self.assertEqual(merged[0]["detalhes_completos"], "agora sim")

    def test_ignores_items_without_link(self):
        merged = merge_procedimentos_by_link(
            [{"entidade": "sem link"}],
            [{"link": "https://dre.pt/a", "entidade": "A"}],
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["link"], "https://dre.pt/a")

    def test_existing_complete_by_link_skips_incomplete(self):
        items = [
            {"link": "https://dre.pt/a", "detalhes_completos": "ok"},
            {"link": "https://dre.pt/b"},
        ]
        cache = existing_complete_by_link(items)
        self.assertIn("https://dre.pt/a", cache)
        self.assertNotIn("https://dre.pt/b", cache)


class TestLoadJsonList(unittest.TestCase):
    def test_missing_file(self):
        self.assertEqual(load_json_list("/tmp/does-not-exist-dre.json"), [])

    def test_valid_list(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write('[{"link": "https://dre.pt/a"}]')
            path = f.name
        try:
            self.assertEqual(load_json_list(path), [{"link": "https://dre.pt/a"}])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
