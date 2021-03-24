# The git wiki "creator" - actually it doesn't create a wiki only a git repo of the pages
#

import os
import subprocess
import shutil

class WikiCreator:

    def __init__(self, converter, log):
        self.commands = []
        self.converter = converter
        self.log = log

    # Actual API
    def init(self):
        self.commands.append('git init --quiet')
        pass

    def create_dir(self, dirname):
        self.commands.append('mkdir -p "%s"' % dirname)

    def decompress(self, filename, txtfile):
        self.commands.append('gunzip -c "%s" > "%s"' % (filename, txtfile))

    def convert(self, txtfile, mdfile):
        self.commands.append('dokuwiki2md "%s" > "%s"' %
                             (txtfile, mdfile))

    def add(self, mdfile):
        self.commands.append('git add "%s"' % mdfile)

    def delete(self, mdfile):
        self.commands.append('git rm --quiet "%s"' % mdfile)

    def clean(self, filename):
        self.commands.append('rm "%s"' % filename)

    def commit(self, author, timestamp, message):
        self.commands.append('git commit --quiet --allow-empty --allow-empty-message --author="%s" --date="%s +0000" -m "%s"' %
                             (author, timestamp, message.replace('"', '\\"')))

    def add_media(self, dirname, fullfile, filename):
        self.commands.append('mkdir -p "%s"' % dirname)
        self.commands.append('cp "%s" "%s"' % (fullfile, filename))
        self.commands.append('git add "%s"' % filename)

    def commit_media(self):
        self.commands.append(
            'git commit --quiet --allow-empty --author="dokuwiki2git <dokuwiki2git@hoxu.github.com>" -m "Import media files"')

    def finish(self, gitdir="gitdir"):
        self.commands.append(
            'git commit --quiet --allow-empty --author="dokuwiki2git <dokuwiki2git@hoxu.github.com>" -m "Dokuwiki data imported by dokuwiki2git"')
        self.create_git_repository(gitdir)

    # Utilities
    def create_git_repository(self, gitdir):
        self.log.info('Creating git repository')
        origdir = os.getcwd()
        shutil.rmtree(gitdir)
        os.mkdir(gitdir)
        os.chdir(gitdir)
        # run all commands
        for c in self.commands:
            self.log.debug('CMD: %s' % c)
            ret = subprocess.call(c, shell=True)
            if ret != 0:
                raise RuntimeError('Command "%s" failed' % c)
        os.chdir(origdir)
