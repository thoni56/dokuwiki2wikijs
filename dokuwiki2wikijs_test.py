import unittest

from dokuwiki2wikijs import first_heading_or_filename, convert_filename_to_unicode


class Dokuwiki2WikijsTest(unittest.TestCase):

    def test_get_title(self):
        lines = ["# Title"]
        self.assertEqual(first_heading_or_filename(lines, ""), "Title")

        lines = ["# Title with spaces"]
        self.assertEqual(first_heading_or_filename(
            lines, ""), "Title with spaces")

        lines = ["some other text on the first line"]
        self.assertEqual(first_heading_or_filename(
            lines, "Some other title"), "Some other title")

    def test_convert_to_unicode(self):
        self.assertEqual(convert_filename_to_unicode(
            "a%C3%96bcdef"), "aÖbcdef")
        self.assertEqual(convert_filename_to_unicode(
            "abc%C3%B6def"), "abcödef")
        self.assertEqual(convert_filename_to_unicode(
            "a%C3%B6bcdef"), "aöbcdef")
