import re
import urllib
import requests
import argparse
from time import sleep
from html import unescape
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


DEFAULT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'
EXCLUDE_TYPES = [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".zip", ".rar", ".tar", ".gz", ".mp3", ".mp4", ".avi", ".wmv", ".jsp"]
DELAY = 0
VERBOSE = False


class SiteBrowser:
    def __init__(self, url):
        self.url = url
        parsed_url = urllib.parse.urlparse(url, scheme='', allow_fragments=True)
        self.scheme = parsed_url.scheme
        self.domain = parsed_url.netloc
        self.emails = []
        self.explored_paths = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-agent':DEFAULT_HEADER
        })

    def dispatch_response(self, url):
        if VERBOSE:
            print('[i] Browsing: ' + url)
        html = unescape(self.session.get(url).text)
        soup = BeautifulSoup(html, 'html.parser')
        return [html, soup]

    def get_site_emails(self, text):
        email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        emails = list(set(email for email in re.findall(email_pattern, text) if not any(email.endswith(filetype) for filetype in EXCLUDE_TYPES)))
        if VERBOSE:
            for email in emails:
                print('[+] Found email: ' + email)
        return emails

    def get_site_paths(self, soup):
        return set(link.get('href') for link in soup.find_all('a') if (self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc)) and not any(link.get('href').endswith(filetype) for filetype in EXCLUDE_TYPES))

    def scrap_emails(self, depth, max, delay):
        try:
            html, soup = self.dispatch_response(self.url)
        except RequestException:
            return []
        self.emails = self.get_site_emails(html)
        visited_paths = {self.url}
        next_paths = {self.url}
        nreqs = 0
        while depth > 0:
            paths = next_paths
            next_paths = set()
            for path in paths:
                if nreqs >= max and max != 0:
                    depth = 0
                    break
                sleep(delay)
                visited_paths.add(path)
                try:
                    html, soup = self.dispatch_response(path)
                except RequestException:
                    depth = 0
                    break
                nreqs += 1
                new_emails = self.get_site_emails(html)
                self.emails += new_emails
                for link in set(self.get_site_paths(soup)):
                    if link not in visited_paths:
                        next_paths.add(link)
            depth = depth - 1
        return list(set(self.emails))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('urls', metavar='URL', type=str, nargs='+', help='A list of one or more URLs')
    parser.add_argument('--print', dest='print', action='store_true', help='Print the URLs at the end.')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Print browsed URLs.')
    parser.add_argument('--depth', dest='depth', type=int, default=1, help='Depth of search ramifications. 0 means no recursion.')
    parser.add_argument('--max', dest='max', type=int, default=0, help='The total maximun number of requests to send for each root URLs.')
    parser.add_argument('--delay', dest='delay', default=0, type=int, help='Delay in seconds after each request.')
    parser.add_argument('--output', dest='output', type=str, help='The file path for the found emails.')
    args = parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose
    depth = args.depth + 1
    emails = []
    if not args.output:
        args.print = True
    for url in args.urls:
        if not urllib.parse.urlparse(url).scheme:
            try:
                url = 'https://'+url
                requests.get(url)
            except RequestException:
                url = 'http://'+url
                try:
                    requests.get(url)
                except RequestException:
                    print('[!] Failed to get site ('+ args.url +') both with HTTP and HTTPS.')
                    break
        site = SiteBrowser(url)
        emails += site.scrap_emails(depth, args.max, args.delay)
    if emails and args.print:
        print('\nFound ' + str(len(emails)) + ' emails:')
        for email in emails:
            str_line = "[+] Found email from " + site.domain + " -> " + email
            print(str_line)
    if args.output:
        with open(args.output, "w") as f:
            for url in args.urls:
                f.write(url + "\n")


if __name__ == '__main__':
    main()