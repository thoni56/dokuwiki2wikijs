# dokuwiki2wikijs

We wanted to migrate from dokuwiki to the more modern Wiki.js so this is a script that does some of that work.

It converts all current pages to Markdown using `pandoc`, storing them in the same structure as the `dokuwiki` installation.

This README might not be completely up-to-date and the code quality not up to standard since this is a script for our own use. (Although you are welcome to use and modify it.)

The current version will do the conversion and zip all markdown files for file storage import into Wiki.js.
It does not handle media.

An alternative strategy would be to use the API.
We have not explored that.

# Features

- Convert latest version of `dokuwiki` pages into markdown
- Point to a dokuwiki installation to get a zip of the complete page tree
- Point to a single file and get the conversion of that on stdout
- Transparent handling of any potention `markdowku` pages (an extension to `dokuwiki` which can render markdown "natively" so they are stored as markdown)
- Converts Dokuwiki links in Markdown pages to Markdown format
- Uses the first line, if it is a heading, for the title meta-data, if not the basename of the file is used instead
- Un-mangle Unicode paths (`%C3B6` etc) back to genuine unicode
- Convert basic WRAP tags to `> text{.is-<kind>}` (blockquote with CSS)
- Removes some useless tags from plugins (for now just `<sortable>`)

## Conversion

We had the `markdowku` plugin activated, which seemed to be a good idea when editing pages.
So we had both Dokuwiki pages and Markdown pages.
This script decides how to handle the actual conversion based on the first character in the page.
If it's a `#` the page is _not_ sent for `pandoc` conversion, but kept as-is, assuming it is already Markdown.

The problem when migrating became that the pages could contain a mix of Markdown and Dokuwiki syntax, e.g. markdown unordered lists (line starting with a dash) is not "legal" dokuwiki, and are thus considered text by `pandoc -f dokuwiki ...`.
We decided to fix most of these on the source side by either reverting to pure Dokuwiki or ensuring the whole page was Markdown only.

A very common problem is that internal links in Markdown pages are still in Dokuwiki format because of the built-in support in the editor.
The script tries to convert those links in markdown-pages to markdown format to mimimize manual conversion work.

# Limitations

It does not handle mixed (dokuwiki and markdown) content well.
No post-processing of markup pages is performed except for the tags and links as described under "Features".

It does not (at this time) convert media files.

# Prerequisites

- Python3
- Pandoc with multimarkdown (don't know if that is included by default)

# Usage

- run the script with the path to a dokuwiki installation as the argument
- see the conversion run and get a zip-file of the converted page tree in your current directory
- unpack the zip in a Wiki.js file storage (which you need to have set up) and press "Import Everything"

or

- run the script with the path to a dokuwiki page as the argument
- get the converted page on the stdout

# Wanted features

- Remove unnecessary tags (like from extensions) and/or convert others
    - ~~`<sortable>` is done~~
    - ~~`<wrap>` could be converted to blockquote (`> `) and `</wrap>` to `{.is-<type>}` where `type` is given by opening `<wrap>`~~
    - ...
- Convert to "one sentence per line" convention where possible (This partially implemented, but turned out to complex with a simple minded approach)
- Flag wrong internal links since pandoc can only correctly convert internal links if the double square brackets contain an existing page path, if it is to the "titel" of a page the link will be broken.
Don't know how to fix them...
- Make un-mangling of filenames an option
- Handle media, which is a completely unchartered territory since I don't know how to import media into wiki.js...

# Notes

- At one point we tried to build upon [dokuwiki2git](https://github.com/hoxu/dokuwiki2git) since Wiki.js has an option to use git as a backing store. However it turned out that it would just import the latest version of every page anyway. Neither did it use the user info from the commits, all pages will be created by whoever does the import anyway. There was just no benefits over a simple file storage. So we went back to just handling the current version of the pages.

- Dokuwiki have multiple ways to find the page for a folder

    - page with the same name as the folder ('folder.txt' in the same directory as 'folder')
    - 'start.txt' in the folder ('folder/start.txt')
    - page with the same name as the folder _in the folder_ ('folder/folder.txt')

    We were thinking about automatically fixing this in the script. But there might actually be conflicts here, so we decided on manually adjust the original structure so that all the occurences used a consistent, and also the (upcoming) Wiki.js, way, namely 'folder.txt' parallel to 'folder'.

- Page titles with just numbers don't work. We decided to fix this at the source too.
