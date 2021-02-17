#! /usr/bin/env python3

import os
import sys
from zipfile import ZipFile
from os.path import basename
from shutil import copyfile
import subprocess


def pandoc(infile):
    result = subprocess.run(
        ["pandoc", "-f", "dokuwiki", "-t", "markdown_mmd", infile], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def first_heading_or_filename(lines, pagename):
    if lines[0][0] == '#':
        title = lines[0].partition(' ')[2].strip()
    else:
        title = pagename
    return title


def get_metadata(lines, pagename):
    return {
        "title": first_heading_or_filename(lines, pagename)
    }


def add_metadata(lines, metadata):
    lines.insert(0, "---")
    for key, value in metadata.items():
        lines.insert(1, key+": "+value)
    lines.insert(len(metadata)+1, "---")


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


def read_users():
    users_file = os.path.join('conf', 'users.auth.php')
    with open(users_file, 'r') as f:
        for line in f:
            if not line.startswith("#") and len(line) > 1:
                userparts = line.split(':')
                assert(len(userparts) == 5)
                users[userparts[0]] = {
                    'name': userparts[2], 'email': userparts[3]}


def remove_useless_tags(lines):
    new_lines = []
    for line in lines:
        line = line.replace('\\<sortable\\>', '')
        line = line.replace('\\</sortable\\>', '')
        new_lines.append(line)
    return new_lines


def convert_file(txtfile):
    if is_markdown(txtfile):
        with open(txtfile) as file:
            lines = file.readlines()
    else:
        lines = str(pandoc(txtfile)).split('\n')
    lines = remove_useless_tags(lines)
    metadata = get_metadata(lines, basename)
    add_metadata(lines, metadata)

    return lines


if __name__ == "__main__":

    if len(sys.argv) > 1:
        lines = convert_file(sys.argv[1])
        print('\n'.join(lines))
    else:
        if not os.path.exists("data/pages"):
            print("Current directory should be at the root of a dokuwiki installation")
            sys.exit(-1)

        users = {}
        read_users()

        for folder, _, files in os.walk(os.path.join(os.path.curdir, "data/pages")):
            txt_files = (file for file in files if file.endswith(".txt"))
            for f in txt_files:
                filename_with_txt = os.path.join(folder, f)
                filename = convert_filename_to_unicode(filename_with_txt[:-4])
                basename = os.path.basename(filename)
                ensure_path_exists(filename)

                print(filename_with_txt+"("+basename+"):", end="")

                lines = convert_file(filename_with_txt)

                filename_with_md = filename+".md"
                with open(filename_with_md, "w") as file:
                    file.writelines(lines)

                print(len(lines))

        with ZipFile("dokuwiki2wikijs.zip", 'w') as zipObj:
            # Walk through the files in a directory
            for folder, folders, files in os.walk(os.path.curdir):
                files = (file for file in files if file.endswith(".md"))
                for file in files:
                    zipObj.write(os.path.join(folder, file))
        print("'dokuwiki2wikijs.zip' created\n")
