# The git wiki "creator" - actually it doesn't create a wiki only a git repo of the pages
#

class GitWikiCreator:

    # Actual API
    def init(self):
        self.commands.append('git init --quiet')
        pass

    def finish(self):
        pass

    # Utilities necessary during extraction from main program
    def get_commands(self):
        return self.commands
