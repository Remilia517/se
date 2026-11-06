import unittest
from argparse import Namespace

from minicurl.cli import parse_header, _parse_cookies, _parse_forms


class MiniCurlParserTests(unittest.TestCase):
    def test_parse_header(self):
        self.assertEqual(
            parse_header(["Accept: application/json", "X-Test: hello"]),
            {"Accept": "application/json", "X-Test": "hello"},
        )

    def test_invalid_header(self):
        with self.assertRaises(ValueError):
            parse_header(["WrongHeader"])

    def test_parse_cookie(self):
        self.assertEqual(_parse_cookies(["sid=abc", "theme=dark"]),
                         {"sid": "abc", "theme": "dark"})

    def test_invalid_cookie(self):
        with self.assertRaises(ValueError):
            _parse_cookies(["sid"])

    def test_parse_form(self):
        self.assertEqual(_parse_forms(["name=Alice", "age=20"]),
                         {"name": "Alice", "age": "20"})


if __name__ == "__main__":
    unittest.main()
