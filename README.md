# dokuwiki2wikijs

We wanted to migrate from dokuwiki to the more modern Wiki.js so this is a script that tries to do that.

There is a working version in the history, but I have re-started from `dokuwiki2git` script by hoxu to create a git repo with changes that can then be imported into Wiki.js.

NOTE: not working at this point.

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

# Known problems

- Unicode (non-ascii) filenames works badly since dokuwiki seems to have changed the encoding in filenames over the years, and the change records use the unicode but the filenames use a mangled form (%C3%B6 e.g)...
- Pages that have been moved using PageMove(?) are not handled. This script ignores changes that don't match up, so in practice history beyond a PageMove is lost... (A move is recorded by the changes file moved along with the `*.txt` and a 'C' is inserted in the `*.changes` and the changes file for the previous file is replaced with a single 'D' line. So it should be possible to recreate that history too, but we decided it is too much work.)
