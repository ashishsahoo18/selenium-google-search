import unittest

from app import SEARCH_ENGINES, safe_filename


class SearchAppTests(unittest.TestCase):

    def test_supported_engines_have_https_urls(self):
        self.assertTrue(
            all(
                url.startswith("https://")
                for url in SEARCH_ENGINES.values()
            )
        )

    def test_filename_is_safe_for_windows(self):
        result = safe_filename('iphone: 16 / "pro"')
        self.assertEqual(result, "iphone_ 16 _ _pro")

    def test_empty_filename_gets_default(self):
        self.assertEqual(safe_filename("..."), "search")


if __name__ == "__main__":
    unittest.main()
