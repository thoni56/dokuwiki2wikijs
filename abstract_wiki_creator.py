# An abstract version of a Wiki creator backend to dokuwiki2wikijs
#
# As Sandi Metz said extract the variability, and we started out with
# git, and will replace that with a Wiki.js API creator.

class WikiCreator:

    def __init__(self, converter, log):
        pass

    def init(self):
        # Do whatever needs to be done first
        # converter(input, output) - convert input file in dokuwiki format to output in Markdown
        pass

    def create_dir(self, dirname):
        pass

    def decompress(self, filename, txtfile):
        pass

    def convert(self, txtfile, mdfile):
        pass

    def add(self, mdfile):
        pass

    def delete(self, mdfile):
        pass

    def clean(self, filename):
        pass

    def commit(self, author, timestamp, message):
        pass

    def add_media(self, dirname, fullfile, filename):
        pass

    def commit_media(self):
        pass

    def finish(self):
        # Do whatever needs to be done last
        pass
