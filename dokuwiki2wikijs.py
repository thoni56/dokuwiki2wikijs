#!/usr/bin/env python
#
# This script is built on the dokuwiki2git script by Heikki Hokkanen <hoxu at users.sf.net>
# as specified by its license: AGPLv3

import fnmatch
import logging
import optparse
import os
import sys
import time
from dokuwiki2md import convert_dokuwiki_file_to_md

# Use one wiki creator backend
import git_wiki_creator as wc

USAGE = """
NOTE: Experimental and non-complete...

dokuwiki2wikijs converts a dokuwiki installation into a git repository containing
the wiki pages, with proper history, in markdown format, to be used as input data for
a Wiki.js site.

$ dokuwiki2wikijs [options] /path/to/dokuwiki"""

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
log = logging.getLogger()


def convert_to_md(infile, outfile):
    lines = convert_dokuwiki_file_to_md(infile)
    with open(outfile, "w") as f:
        f.writelines(lines)


creator = wc.WikiCreator(convert_to_md, log)


class Converter:
    def __init__(self):
        self.datadir = None
        self.atticdir = None
        self.mediadir = None
        self.metadir = None
        self.confdir = None
        # (timestamp, ip, changetype, pagename, author, currentpagepath
        self.changelog = []
        self.commands = []  # commands to run to create the git repository
        self.gitdir = 'gitdir'
        self.users = {}

    def get_pagepath_and_timestamp(self, filename):
        filename = os.path.relpath(filename, self.atticdir)
        parts = filename.rsplit('.', 3)
        return parts[0], parts[1]  # pagepath, filename

    def has_changelog_entry(self, pagepath, timestamp):
        for c in self.changelog:
            ts = c[0]
            pagename = c[3]
            if timestamp == ts and pagepath == pagename.replace(':', '/'):
                return
        log.warning('Attic contains "%s" timestamp %s, but it is not referenced by any changelog, skipping. Please report this!' % (
            pagepath, timestamp))

    def read_attic(self):
        log.info('Reading attic')

        # Check that all referenced pages exist in attic
        for c in self.changelog:
            pagepath = c[3].replace(':', '/')
            filename = os.path.join(
                self.atticdir, pagepath + '.%s.txt.gz' % c[0])
            if not os.path.exists(filename):
                log.warning(
                    'File "%s" does not exist, despite being in changelog (%s), skipping' % (filename, c[6]))
                continue

            # depending on type of change, either add or remove
            pagepath, timestamp = self.get_pagepath_and_timestamp(filename)
            txtfile = pagepath + '.txt'
            mdfile = pagepath + '.md'
            message = pagepath + ': ' + c[5]
            user = c[4]
            email = 'dokuwiki@%s' % (c[1])
            if len(user) == 0:
                user = 'dokuwiki2git'
            elif user in self.users:
                email = self.users[user]['email']
                user = self.users[user]['name']
            author = '%s <%s>' % (user, email)
            if c[2] in ('C', 'E', 'e', 'R'):  # create, edit, minor edit, restore
                dirname = os.path.dirname(txtfile)
                if len(dirname) > 0:
                    creator.create_dir(dirname)
                creator.decompress(filename, txtfile)
                creator.convert(txtfile, mdfile)
                creator.add(mdfile)
                creator.clean(txtfile)
            elif c[2] == 'D':  # delete
                creator.delete(mdfile)
            creator.commit(author, timestamp, message)

        # check that all pages in attic have a matching changelog entry
        for path, dirs, files in os.walk(self.atticdir):
            for f in files:
                if fnmatch.fnmatch(f, '*.txt.gz'):
                    filename = os.path.join(path, f)
                    pagepath, timestamp = self.get_pagepath_and_timestamp(
                        filename)
                    self.has_changelog_entry(pagepath, timestamp)

    def read_media(self):
        log.info('Reading media')
        for path, dirs, files in os.walk(self.mediadir):
            for f in files:
                fullfile = os.path.join(path, f)
                filename = os.path.relpath(fullfile, self.datadir)
                dirname = os.path.dirname(filename)
                creator.add_media(dirname, fullfile, filename)
        creator.commit_media()

    def read_meta(self):
        log.info('Reading meta')
        pages = 0
        for path, dirs, files in os.walk(self.metadir):
            for f in files:
                if fnmatch.fnmatch(f, '*.changes'):
                    relpath = os.path.relpath(
                        os.path.join(path, f), self.metadir)
                    pagepath = relpath.rsplit('.', 1)[0]
                    self.read_meta_for_page(pagepath, os.path.join(path, f))
                    pages += 1
        log.info('%d changelog entries for %d pages found' %
                 (len(self.changelog), pages))

    def read_data(self):
        creator.init()
        # find user Real Name and email
        self.read_user_data()
        # go through data/meta
        self.read_meta()
        # sort history
        self.changelog.sort()
        # go through data/attic, importing pages referenced by .changes in meta
        self.read_attic()
        self.read_media()

    def demangle(self, pagename):
        # TODO for now only convert cases that we have in our wiki
        pagename = pagename.replace("%C3%84", "Ä")
        pagename = pagename.replace("%C3%85", "Å")
        pagename = pagename.replace("%C3%96", "Ö")
        pagename = pagename.replace("%C3%A4", "ä")
        pagename = pagename.replace("%C3%A5", "å")
        pagename = pagename.replace("%C3%B6", "ö")
        return pagename

    def read_meta_for_page(self, pagepath, fullpath):
        if pagepath in ('_dokuwiki', '_comments', '_media'):
            return
        pagename = pagepath.replace('/', ':')

        # In .changes there are unicode characters, but the files have mangled unicode names ('%C3%B6')
        pagename = self.demangle(pagename)

        log.debug('Reading meta for page "%s"' % pagename)
        with open(fullpath, 'r') as f:
            for l, line in enumerate(f):
                changeparts = line.split('\t')
                log.debug(changeparts)
                if changeparts[6] == '':
                    changeparts.remove('')
                assert(len(changeparts) == 7)
                changeparts[3].replace('\\x', '%')
                if changeparts[3] != pagename:
                    # Might be a page that has been moved with PageMove because history with old name is retained in .changes
                    log.debug("Pagename mismatch in metadata for " +
                              pagepath + " (vs. " + changeparts[3] + ") on line " + str(l) + " in " + fullpath)
                # else:
                # create, delete, edit, minor edit, restore
                assert(changeparts[2] in ('C', 'D', 'E', 'e', 'R'))
                changeparts[6] = pagepath
                self.changelog.append(changeparts)

    def read_user_data(self):
        log.info('Reading users.auth.php')
        users_file = os.path.join(self.confdir, 'users.auth.php')
        with open(users_file, 'r') as f:
            for line in f:
                if not line.startswith("#") and len(line) > 1:
                    userparts = line.split(':')
                    assert(len(userparts) == 5)
                    log.debug(userparts)
                    self.users[userparts[0]] = {
                        'name': userparts[2], 'email': userparts[3]}
        log.info('Read %d users' % len(self.users))

    def run(self, params):
        parser = optparse.OptionParser(usage=USAGE)
        parser.add_option('-o', '--output', dest='outputdir',
                          help='Create git directory at outputdir. Default is "gitdir"', default='gitdir')
        parser.add_option('-q', '--quiet', action='store_const', const=0,
                          dest='verbose', help='Show only errors')
        parser.add_option('-v', '--verbose', action='store_const', const=2,
                          dest='verbose', help='Show debug messages', default=1)
        (options, args) = parser.parse_args(params)
        level = logging.ERROR
        if options.verbose:
            level = (logging.WARNING, logging.INFO,
                     logging.DEBUG)[options.verbose]
        log.setLevel(level)
        self.gitdir = options.outputdir

        time_start = time.time()
        if len(args) == 0:
            parser.print_help()
            log.error('Dokuwiki data directory is a required argument')
            sys.exit(1)

        self.set_datadir(args[0])
        self.read_data()

        creator.finish(self.gitdir)

        time_end = time.time()
        time_took = time_end - time_start
        log.info('Finished converting dokuwiki data dir "%s" into a git repository "%s", took %.2f seconds' % (
            self.datadir, self.gitdir, time_took))

    def set_datadir(self, dir):
        if not is_dokuwiki_dir(dir):
            raise RuntimeError(
                'Directory "%s" does not look like a dokuwiki installation' % dir)
        self.datadir = os.path.abspath(os.path.join(dir, 'data'))
        self.metadir = os.path.join(self.datadir, 'meta')
        self.atticdir = os.path.join(self.datadir, 'attic')
        self.mediadir = os.path.join(self.datadir, 'media')
        self.confdir = os.path.join(dir, 'conf')
        log.info('Using datadir: %s' % self.datadir)


def is_dokuwiki_dir(dir):
    return isdir(dir, 'data') and isdir(dir, 'conf') and isdir(dir, 'data/pages') and isfile(dir, 'data/_dummy')


def isdir(dir, dir_subpath):
    return os.path.isdir(os.path.abspath(os.path.join(dir, dir_subpath)))


def isfile(dir, file_subpath):
    return os.path.isfile(os.path.abspath(os.path.join(dir, file_subpath)))


if __name__ == '__main__':
    c = Converter()
    c.run(sys.argv[1:])
