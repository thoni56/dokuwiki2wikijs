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


if __name__ == "__main__":
    if not os.path.exists("data/pages"):
        print("Current directory should be at the root of a dokuwiki installation")
        sys.exit(-1)

    for folder, _, files in os.walk(os.path.join(os.path.curdir, "data/pages")):
        txt_files = (file for file in files if file.endswith(".txt"))
        for f in txt_files:
            filename_with_txt = os.path.join(folder, f)
            filename_with_txt_md = filename_with_txt+".md"
            filename = convert_filename_to_unicode(filename_with_txt[:-4])
            basename = os.path.basename(filename)
            ensure_path_exists(filename)

            print(filename_with_txt+"("+basename+"):", end="")

            if is_markdown(filename_with_txt):
                copyfile(filename_with_txt, filename_with_txt_md)
            else:
                convert_to_markdown(filename_with_txt, filename_with_txt_md)

            file = open(filename_with_txt_md)
            lines = file.readlines()

            use_first_heading_or_filename_as_title(lines, basename)

            filename_with_md = filename+".md"
            with open(filename_with_md, "w") as file:
                file.writelines(lines)

            print(len(lines))
            os.remove(filename_with_txt_md)

    with ZipFile("dokuwiki2wikijs.zip", 'w') as zipObj:
        # Walk through the files in a directory
        for folder, folders, files in os.walk(os.path.curdir):
            files = (file for file in files if file.endswith(".md"))
            for file in files:
                zipObj.write(os.path.join(folder, file))
    print("'dokuwiki2wikijs.zip' created\n")
