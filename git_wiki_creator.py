# The git wiki "creator" - actually it doesn't create a wiki only a git repo of the pages
#

class WikiCreator:

    def __init__(self, converter):
        self.commands = []
        self.converter = converter

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

    def finish(self):
        self.commands.append(
            'git commit --quiet --allow-empty --author="dokuwiki2git <dokuwiki2git@hoxu.github.com>" -m "Dokuwiki data imported by dokuwiki2git"')

    # Utilities necessary during extraction from main program
    def get_commands(self):
        return self.commands
