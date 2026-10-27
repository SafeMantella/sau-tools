import unittest

import yt


class T(unittest.TestCase):
    def test_upload_args_default_to_private_so_nothing_goes_public_by_accident(self):
        a = yt.parser().parse_args(["upload", "--file", __file__, "--title", "t"])
        self.assertEqual(a.visibility, "private")
        self.assertFalse(a.dry_run)

    def test_upload_is_done_when_the_progress_label_has_no_percent(self):
        self.assertFalse(yt.upload_done(""))
        self.assertFalse(yt.upload_done("Fazendo upload... 76%"))
        self.assertTrue(yt.upload_done("Processando HD..."))

    def test_visibility_maps_to_studio_radio_names(self):
        self.assertEqual(yt.RADIO, {"public": "PUBLIC", "unlisted": "UNLISTED", "private": "PRIVATE"})


if __name__ == "__main__":
    unittest.main()
