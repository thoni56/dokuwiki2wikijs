# dokuwiki2wikijs

This script does a crude export and conversion of all current pages and media files of a Dokuwiki installation and prepares it for import to Wiki.js.

It converts all current pages to Markdown using `pandoc`, stores them in the same structure as the `dokuwiki` installation and then zips that structure, making all converted pages and media ready for transfer to a Wiki.js installation.

# Features

- Convert latest version of `dokuwiki` pages into markdown
- Point to a dokuwiki installation to get a zip of the complete page tree
- Point to a single file and get the conversion of that on stdout to see if it needs manual adjustments
- Transparent handling of any potention `markdowku` pages (an extension to `dokuwiki` which can render markdown "natively" so they are stored as markdown)
- Converts Dokuwiki links in Markdown pages to Markdown format
- Uses the first line, if it is a heading, for the title meta-data, if not, the basename of the file is used instead
- Un-mangle paths with (some) Unicode characters (`%C3%B6` etc) back to genuine unicode
- Convert basic WRAP (plugin) tags to `> text{.is-<kind>}` (blockquote with CSS)
- Removes some useless tags from plugins (for now just `<sortable>`)

## Conversion caveats

### Markdowku

We had the `markdowku` plugin activated, which seemed to be a good idea when editing pages.
So we had both Dokuwiki pages and Markdown pages.

This script decides how to handle the actual conversion based on the first character in the page.
If it's a `#` the page is _not_ sent for `pandoc` conversion, but kept as-is, assuming it is already Markdown.

What's more, the `markdowku` plugin is implemented in such a way that it is possible to mix markdown and dokuwiki formatting in the same page.
So pages may contain a mix of Markdown and Dokuwiki syntax and still render correctly in Dokuwiki.
But it trashes conversion, e.g. Markdown unordered lists (line starting with a dash) is not "legal" dokuwiki, and are thus considered text by `pandoc -f dokuwiki ...`.
This is impossible to handle, unless you re-implement the full dokuwiki content parsing pipeline.
(Although piggy-backing directly on the actual dokuwiki source might be the "correct" way to do this conversion...)

This script makes no attempt to handle or signal this situation.
Instead we decided to fix most of these on the source side by either reverting to pure Dokuwiki or ensuring the whole page was Markdown only.
This might be prohibitive if you have a huge site with mixed pages.

As the editor always inserts Dokuwiki formatted page links, even "well formed" markdown pages will contain dokuwiki links.
Thus, the script converts dokuwiki links in markdown-pages to markdown format to mimimize manual conversion work.

### Folder page files

Dokuwiki have multiple ways to find the page to show for a folder "node":

- page with the same name as the folder ('folder.txt' in the same directory as 'folder')
- 'start.txt' in the folder ('folder/start.txt')
- page with the same name as the folder _in the folder_ ('folder/folder.txt')

We were thinking about automatically fixing this in the script.
But there might actually be conflicts here, so we decided on manually adjusting the original structure so that all the occurences used a consistent, and also the (upcoming) Wiki.js, way, namely 'folder.txt' parallel to 'folder'.

### Page titles

Page titles with only numbers don't import.
We decided to fix this at the source too.

### Page authors

Importing pages through the file storage will set author to the person logged in when doing the import.
No author information will be transfered when using this script.

### Links spanning multiple lines

Although dokuwiki have no problem handling links that are broken over two lines, e.g between spaces in the text, this script cannot handle that.

# Limitations

- It does not handle mixed content (pages that contain both dokuwiki and markdown formatting).
- No post-processing of markdown pages is performed except for the tags and links as described under "Features".

# Prerequisites

- Python3
- Pandoc with multimarkdown (don't know if that is included by default)

# Usage

## Single page conversion

To see the resulting conversion of a single page run the script with the page as the argument, e.g.

    > dokuwiki2wikijs /var/www/dokuwiki/data/pages/start.txt

The rendered result will be output to standard output and can be piped to a file.

## Installation conversion

To convert a complete installation run the script with the root of the installation as argument, e.g.

    > dokuwiki2wikijs /var/www/dokuwiki

You then get a zip-file with the converted pages and media in your current directory.

Setup a Local File System storage in your Wiki.js installation.
Watch out for where Wiki.js can actually create the directory, `/tmp/wiki` is a safe bet.
Unpack the zip in a Wiki.js in that directory.
If you are running Wiki.js in a Docker container these are the steps to do that:

    > docker cp dokuwiki2wikijs.zip <container>:/tmp
    > docker exec -it <container> /bin/bash
    # cd <file storage folder>
    # unzip /tmp/dokuwiki2wikijs.zip

- Ensure that you have your wanted locale set in Wiki.js.
- In your Wiki.js `Storage/Local File System` settings press "Import Everything" and wait.
- Re-render all pages (`Settings/Tools/Content/Re-render all pages`) to ensure links are updated.
- Done.

# Wanted features

- Remove unnecessary tags (like from extensions) and/or convert others
  - ~~`<sortable>` should be removed. Done.~~
  - ~~`<wrap>` could be converted to blockquote (`>`) and `</wrap>` to `{.is-<type>}` where `type` is given by opening `<wrap>`. Done.~~
  - ...
- Import date information.
- Convert to "one sentence per line" convention where possible. This is partially implemented, but turned out too complex with a simple minded approach, so we went with using `--wrap=none` for the pandoc conversions. It also turned out that Wiki.js does not render pages with this convention correctly (it keeps the line breaks as hard breaks).
- Flag wrong internal links since pandoc can only correctly convert internal links if the double square brackets contain an existing page path, if it is to the "titel" of a page the link will become broken.
- Make un-mangling of filenames an option.
- Import only media which is actually referenced.

# Alternate approaches

Just converting the current version of pages and then import them through the file storage mechanism with all pages created by the one running the import, did not feel sufficient.
So here are a number of alternate approaches we explored.

## dokuwiki2git

At one point we tried to build upon [dokuwiki2git](https://github.com/hoxu/dokuwiki2git) since Wiki.js has an option to use git as a backing store.
However it turned out that if you just hook up the repo it would just import the latest version of every page anyway.
Neither did it use the user info from the commits, all pages would be created by whoever did the import anyway.
We could not find any benefits over a simple file storage, so we went back to just handling the current version of the pages.

Another problem with using `dokuwiki2git` as the base is that it did not handle page moves.
Instead it gets confused about (older) files that are no longer available.
To do this correctly you need to unwind the history of a page in the same way as `dokuwiki`s own history function does.

So we just scrapped that idea for our migration attempt and was satisfied with importing the last version.
There is a branch `use_docuwiki2git` that holds the code from that attempt.

The major benefit that we thought that we could get from git approach, was importing history and author information.
It did not.

## Wiki.js GraphQL API

We thought that to do a real conversion, with history and author information, we need to go through the API.
It's a GraphQL API and doesn't look to hard.
Once you understand how to explore and use such an API...

It turned out that the API does not allow you to set the author either.
The only way, currently, to set author is through database operations.

So the GraphQL API gave no extra benefits.

## Database import

This seems to be the only real option if you want to keep author and revision information.
We have not explored this since it requires detailed information about the database which does not seem to be available at this time.
