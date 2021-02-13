import unittest

from dokuwiki2wikijs import unquote_markdown_headings

class Dokuwiki2WikijsTest(unittest.TestCase):

    def test_unquote_markdown_headings(self):
        lines = ["\\# Heading", " Not first \\# on line"]

        unquote_markdown_headings(lines)
        self.assertEqual(lines[0], "# Heading")

