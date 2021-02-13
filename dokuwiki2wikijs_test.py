import unittest

from dokuwiki2wikijs import unquote_markdown_headings, use_first_heading_or_filename_as_title, convert_filename_to_unicode

class Dokuwiki2WikijsTest(unittest.TestCase):

    def test_unquote_markdown_headings(self):
        lines = ["\\# Heading", " Not first \\# on line"]

        unquote_markdown_headings(lines)
        self.assertEqual(lines[0], "# Heading")

    def test_insert_title(self):
        lines = ["# Title"]
        use_first_heading_or_filename_as_title(lines, "")
        self.assertEqual(lines[1], "title: Title\n")

        lines = ["# Title with spaces"]
        use_first_heading_or_filename_as_title(lines, "")
        self.assertEqual(lines[1], "title: Title with spaces\n")

        lines = ["some other text on the first line"]
        use_first_heading_or_filename_as_title(lines, "Some other title")
        self.assertEqual(lines[1], "title: Some other title\n")

    def test_convert_to_unicode(self):
        self.assertEqual(convert_filename_to_unicode("a%C3%96bcdef"), "aÖbcdef")
        self.assertEqual(convert_filename_to_unicode("abc%C3%B6def"), "abcödef")
        self.assertEqual(convert_filename_to_unicode("a%C3%B6bcdef"), "aöbcdef")
