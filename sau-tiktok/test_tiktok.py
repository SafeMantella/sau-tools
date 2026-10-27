import unittest
from datetime import datetime
from pathlib import Path

import tiktok


class T(unittest.TestCase):
    def test_logged_in_needs_tiktok_sessionid(self):
        self.assertFalse(tiktok.logged_in([]))
        self.assertFalse(tiktok.logged_in([{"name": "sessionid", "domain": ".google.com"}]))
        self.assertFalse(tiktok.logged_in([{"name": "ttwid", "domain": ".tiktok.com"}]))
        self.assertTrue(tiktok.logged_in([{"name": "sessionid", "domain": ".tiktok.com"}]))

    def test_video_is_visible_chrome_and_immediate_by_default(self):
        f = Path(__file__)  # qualquer arquivo existente
        a = tiktok.parser().parse_args(["upload-video", "--file", str(f), "--title", "oi", "--tags", "a,b"])
        v = tiktok.video(a)
        self.assertFalse(v.headless)
        self.assertEqual(v.local_executable_path, tiktok.CHROME)
        self.assertEqual(v.tags, ["a", "b"])
        self.assertEqual(v.publish_date, 0)
        self.assertTrue(str(v.account_file).endswith("cookies/tiktok_pedro.json"))

    def test_schedule_becomes_datetime(self):
        f = Path(__file__)
        a = tiktok.parser().parse_args(
            ["upload-video", "--file", str(f), "--title", "oi", "--schedule", "2026-11-01 10:30"])
        self.assertEqual(tiktok.video(a).publish_date, datetime(2026, 11, 1, 10, 30))


class FakeKb:
    def __init__(self): self.keys = []
    async def press(self, k): self.keys.append(k)
    async def insert_text(self, t): self.keys.append("text:" + t)


class FakeEl:
    async def click(self): pass


class FakeLoc:
    def locator(self, _): return FakeEl()


class FakePage:
    def __init__(self): self.keyboard = FakeKb()
    async def wait_for_timeout(self, _): pass


class TitleOnMac(unittest.TestCase):
    def test_select_all_is_cmd_a_so_prefilled_filename_is_cleared(self):
        import asyncio
        f = Path(__file__)
        a = tiktok.parser().parse_args(["upload-video", "--file", str(f), "--title", "oi"])
        v = tiktok.video(a)
        v.locator_base = FakeLoc()
        page = FakePage()
        asyncio.run(v.add_title_tags(page))
        self.assertIn("Meta+A", page.keyboard.keys)
        self.assertNotIn("Control+A", page.keyboard.keys)


if __name__ == "__main__":
    unittest.main()
