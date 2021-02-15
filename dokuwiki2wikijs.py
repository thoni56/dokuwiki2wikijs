#!/usr/bin/env python
# Copyright (c) 2011-2014 Heikki Hokkanen <hoxu at users.sf.net>
# License: AGPLv3
import fnmatch
import logging
import optparse
import os
import subprocess
import sys
import time

USAGE = """
dokuwiki2git converts dokuwiki data directory into a git repository containing
the wiki pages, with proper history. Thus, migration to git-backed wiki engines
(eg. gollum) becomes easier.

$ dokuwiki2git [options] /path/to/dokuwiki/data"""

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
log = logging.getLogger()


class Converter:
    def __init__(self):
        self.datadir = None
        self.atticdir = None
        self.mediadir = None
        self.metadir = None
        # (timestamp, ip, changetype, pagename, author, comment)
        self.changelog = []
        self.commands = []  # commands to run to create the git repository
        self.gitdir = 'gitdir'
        self.users = {}

    def create_git_repository(self):
        log.info('Creating git repository')
        origdir = os.getcwd()
        os.mkdir(self.gitdir)
        os.chdir(self.gitdir)
        # run all commands
        for c in self.commands:
            log.debug('CMD: %s' % c)
            ret = subprocess.call(c, shell=True)
            if ret != 0:
                raise RuntimeError('Command "%s" failed' % c)
        os.chdir(origdir)

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
        log.warn('Attic contains "%s" timestamp %s, but is not referenced by changelog, skipping. Please report this!' % (
            pagepath, timestamp))

    def read_attic(self):
        log.info('Reading attic')

        # Check that all referenced pages exist in attic
        for c in self.changelog:
            pagepath = c[3].replace(':', '/')
            filename = os.path.join(
                self.atticdir, pagepath + '.%s.txt.gz' % c[0])
            if not os.path.exists(filename):
                log.warn(
                    'File "%s" does not exist, despite being in changelog, skipping' % filename)
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
            cmds = []
            if c[2] in ('C', 'E', 'e', 'R'):  # create, edit, minor edit, restore
                dirname = os.path.dirname(txtfile)
                if len(dirname) > 0:
                    cmds.append('mkdir -p "%s"' % dirname)
                cmds.append('gunzip -c "%s" > "%s"' % (filename, txtfile))
                cmds.append('dokuwiki2md "%s" > "%s"' %
                            (txtfile, mdfile))
                cmds.append('git add "%s"' % mdfile)
                cmds.append('rm "%s"' % txtfile)
            elif c[2] == 'D':  # delete
                cmds.append('git rm --quiet "%s"' % mdfile)
            cmds.append('git commit --quiet --allow-empty --allow-empty-message --author="%s" --date="%s +0000" -m "%s"' %
                        (author, timestamp, message.replace('"', '\\"')))
            self.commands.extend(cmds)

        # check that all pages in attic have a matching changelog entry
        for path, dirs, files in os.walk(self.atticdir):
            for f in files:
                if fnmatch.fnmatch(f, '*.txt.gz'):
                    filename = os.path.join(path, f)
                    pagepath, timestamp = self.get_pagepath_and_timestamp(
                        filename)
                    self.has_changelog_entry(pagepath, timestamp)

    def read_data(self):
        self.commands.append('git init --quiet')
        # find user Real Name and email
        self.read_user_data()
        # go through data/meta
        self.read_meta()
        # sort history
        self.changelog.sort()
        # go through data/attic, importing pages referenced by .changes in meta
        self.read_attic()
        self.read_media()
        self.commands.append(
            'git commit --quiet --allow-empty --author="dokuwiki2git <dokuwiki2git@hoxu.github.com>" -m "Dokuwiki data imported by dokuwiki2git"')

    def read_media(self):
        log.info('Reading media')
        for path, dirs, files in os.walk(self.mediadir):
            for f in files:
                fullfile = os.path.join(path, f)
                filename = os.path.relpath(fullfile, self.datadir)
                dirname = os.path.dirname(filename)
                cmds = [
                    'mkdir -p "%s"' % dirname,
                    'cp "%s" "%s"' % (fullfile, filename),
                    'git add "%s"' % filename
                ]
                self.commands.extend(cmds)
        self.commands.append(
            'git commit --quiet --allow-empty --author="dokuwiki2git <dokuwiki2git@hoxu.github.com>" -m "Import media files"')

    def read_meta(self):
        log.info('Reading meta')
        pages = 0
        for path, dirs, files in os.walk(self.metadir):
            for f in files:
                if fnmatch.fnmatch(f, '*.changes'):
                    relpath = os.path.relpath(
                        os.path.join(path, f), self.metadir)
                    pagepath = relpath.rsplit('.', 1)[0]
                    self.read_meta_page(pagepath, os.path.join(path, f))
                    pages += 1
        log.info('%d changelog entries for %d pages found' %
                 (len(self.changelog), pages))

    def read_meta_page(self, pagepath, fullpath):
        if pagepath in ('_dokuwiki', '_comments', '_media'):
            return
        pagename = pagepath.replace('/', ':')
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
                    log.warning("Pagename mismatch in metadata for " +
                                pagepath + " (vs. " + changeparts[3] + ") on line " + str(l))
                else:
                    # create, delete, edit, minor edit, restore
                    assert(changeparts[2] in ('C', 'D', 'E', 'e', 'R'))
                    self.changelog.append(changeparts)

    def read_user_data(self):
        log.info('Reading users.auth.php')
        parentdir = os.path.abspath(os.path.join(self.datadir, os.pardir))
        users_file = os.path.join(parentdir, 'conf', 'users.auth.php')
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
                          dest='verbose', help='Show only warnings and errors')
        parser.add_option('-v', '--verbose', action='store_const', const=2,
                          dest='verbose', help='Show debug messages', default=1)
        (options, args) = parser.parse_args(params)
        level = logging.WARN
        if options.verbose:
            level = (logging.WARN, logging.INFO,
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
        log.info('%d commands queued to be executed' % len(self.commands))
        self.create_git_repository()
        time_end = time.time()
        time_took = time_end - time_start
        log.info('Finished converting dokuwiki data dir "%s" into a git repository "%s", took %.2f seconds' % (
            self.datadir, self.gitdir, time_took))

    def set_datadir(self, datadir):
        if not os.path.isfile(os.path.join(datadir, '_dummy')):
            raise RuntimeError(
                'Directory "%s" does not look like a dokuwiki datadir' % datadir)
        self.datadir = os.path.abspath(datadir)
        self.metadir = os.path.join(self.datadir, 'meta')
        self.atticdir = os.path.join(self.datadir, 'attic')
        self.mediadir = os.path.join(self.datadir, 'media')
        log.info('Using datadir: %s' % self.datadir)


if __name__ == '__main__':
    c = Converter()
    c.run(sys.argv[1:])
