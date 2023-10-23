# Recursive Mail Scraper (Remas)

Scraps email addresses from a given URL using recursive search, iterating through links from the same domain name.

## Installation

```
$ git clone https://github.com/alejandrocora/RecursiveMailScraper
$ cd RecursiveMailScraper
$ pip3 install .
```

## Help

```
usage: remas [-h] [--print] [--verbose] [--depth DEPTH] [--max MAX] [--delay DELAY] [--output OUTPUT] URL [URL ...]

positional arguments:
  URL              A list of one or more URLs

options:
  -h, --help       show this help message and exit
  --print          Print the URLs at the end.
  --verbose        Print browsed URLs.
  --depth DEPTH    Depth of search ramifications. 0 means no recursion.
  --max MAX        The total maximun number of requests to send for each root URLs.
  --delay DELAY    Delay in seconds after each request.
  --output OUTPUT  The file path to save the found emails. Emails will be appended.
```