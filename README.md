# Recursive Mail Scraper

Scraps email addresses from a given URL using recursive search, iterating through links from the same domain name.

## Installation

```
$ git clone https://github.com/alejandrocora/RecursiveMailScraper
$ cd RecursiveMailScraper
$ pip3 install .
```

## Help

```
usage: remas [-h] [--print] [--depth DEPTH] [--output OUTPUT] URL [URL ...]

positional arguments:
  URL              A list of one or more URLs

options:
  -h, --help       show this help message and exit
  --print          Print the URLs at the end.
  --verbose        Print browsed URLs.
  --depth DEPTH    Depth of search ramifications.
  --output OUTPUT  The file path for the found emails.
```