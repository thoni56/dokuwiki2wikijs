#! /usr/bin/env python3

import os
import sys
from zipfile import ZipFile
from os.path import basename
from shutil import copyfile


def convert_to_markdown(infile, outfile):
    os.system("pandoc -f dokuwiki -t markdown -o " + outfile + " " + infile)


def use_first_heading_or_filename_as_title(lines, default):
    if lines[0][0] == '#':
        title = lines[0].partition(' ')[2].strip()
    else:
        title = default
    lines.insert(0, "---\n")
    lines.insert(1, "title: "+title+"\n")
    lines.insert(2, "---\n")


def convert_filename_to_unicode(line):
    # Only handles the ones we needed...
    line = line.replace("%C3%84", "Ä")
    line = line.replace("%C3%85", "Å")
    line = line.replace("%C3%96", "Ö")
    line = line.replace("%C3%A4", "ä")
    line = line.replace("%C3%A5", "å")
    line = line.replace("%C3%B6", "ö")
    return line


def ensure_path_exists(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def is_markdown(filename):
    with open(filename) as f:
        first_line = f.readline()
    return first_line[0] == '#'


def convert_dokuwiki_file_to_md(txt_filename):
    basename = os.path.basename(txt_filename)
    md_filename = basename+".md"

    if is_markdown(txt_filename):
        copyfile(txt_filename, md_filename)
    else:
        convert_to_markdown(txt_filename, md_filename)

    with open(md_filename) as file:
        lines = file.readlines()

    use_first_heading_or_filename_as_title(lines, basename)

    return lines


if __name__ == "__main__":
    lines = convert_dokuwiki_file_to_md(sys.argv[1])
    print("".join(lines))
