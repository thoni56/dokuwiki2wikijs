# dokuwiki2wikijs

We wanted to migrate from dokuwiki to the more modern Wiki.js so this is a script that does that.
At least for now it converts pages to Markdown using `pandoc`, storing them in the same structure as the `dokuwiki` installation.
(This might change at some point.)

This README might not be completely up-to-date and the code quality not up to standard since this is a script for our own use. (Although you are welcome to use and modify it.)

The current version will do the conversion and zip all markdown files for file storage import into Wiki.js.

# Features

- Convert latest version of `dokuwiki` pages into markdown
- Point to a dokuwiki installation to get a zip of the complete page tree
- Point to a single file and get the conversion of that on stdout
- Transparent handling of any potention `markdowku` pages (an extension to `dokuwiki` which can render markdown "natively" so they are stored as markdown)
- Uses the first line, if it is a heading, for the title meta-data, if not the basename of the file is used instead
- Un-mangle Unicode filenames (`%C3B6` etc) back to genuine unicode

# Usage

- run the script with the path to a dokuwiki installation
- see the conversion run and get a zip-file of the converted page tree in your current directory
- unpack the zip in a Wiki.js file storage (which you need to have set up) and press "Import Everything"

# Upcoming

- Make un-mangling of filenames an option
- Remove unnecessary tags (like from extensions)
- Convert to "one sentence per line" convention where possible

# Notes

At one point we tried to build upon [dokuwiki2git](https://github.com/hoxu/dokuwiki2git) since Wiki.js has an option to use git as a backing store.
However it turned out that it would just import the latest version of every page anyway.
Neither did it use the user info from the commits, all pages will be created by whoever does the import.
There was just no benefits over a simple file storage.
So we went back to just handling the current version of the pages.
