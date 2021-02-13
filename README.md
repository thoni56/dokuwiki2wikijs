# dokuwiki2wikijs

We wanted to migrate from dokuwiki to the more modern Wiki.js so this is a script that does that.
At least for now it converts pages to Markdown using `pandoc`, storing them in the same structure as the `dokuwiki` installation.
(This might change at some point.)

This README might not be completely up-to-date since this is a script for our own use.
At some point it will probably use part of the `dokuwiki2git` script by ??? to handle easy import into Wiki.js.

The current version will do the conversion and zip all markdown files for file storage import into Wiki.js.

# Features

- Convert latest version of `dokuwiki` pages into markdown
- Transparent handling of any potention `markdowku` pages (it is an extension to `dokuwiki` which can render markdown "natively" so they are stored as markdown)
- Uses the first line, if it is a heading, for the title meta-data, if not the basename of the file is used instead
- Un-mangle Unicode filenames (`%C3B6` etc) back to genuine unicode

# Upcoming

- Use parts of `dokuwiki2git` to also capture history and other metadata and store it in a git repo which can be used as storage for Wiki.js
- Point to a dokuwiki installation rather than use the current directory (avoids permission issues when converting a "live" site)
- Make un-mangling of filenames an option

# Usage

- `cd` into the root of your dokuwiki tree (taking a copy makes everything easier).
- run the script and see the conversion run and a zip-file being created
- unpack the zip in a Wiki.js file storage and press "import" (or something, I forget)
