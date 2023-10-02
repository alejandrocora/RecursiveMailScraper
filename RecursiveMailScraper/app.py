import re
import requests
import urllib
from bs4 import BeautifulSoup
from html import unescape
import argparse


DEFAULT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'
EXCLUDE_TYPES = [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".zip", ".rar", ".tar", ".gz", ".mp3", ".mp4", ".avi", ".wmv", ".jsp"]

verbose = False


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
        html = unescape(self.session.get(url).text)
        soup = BeautifulSoup(html, 'html.parser')
        return [html, soup]

    def get_site_emails(self, text):
        email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        return list(set(email for email in re.findall(email_pattern, text) if not any(email.endswith(filetype) for filetype in EXCLUDE_TYPES)))

    def get_site_paths(self, soup):
        return set(link.get('href') for link in soup.find_all('a') if (self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc)) and not any(link.get('href').endswith(filetype) for filetype in EXCLUDE_TYPES))

    def scrap_emails(self, depth):
        html, soup = self.dispatch_response(self.url)
        self.emails = self.get_site_emails(html)
        visited_paths = {self.url}
        next_paths = {self.url}
        while depth > 0:
            paths = next_paths
            next_paths = set()
            for path in paths:
                visited_paths.add(path)
                if verbose:
                    print('[i] Browsing: ' + path)
                html, soup = self.dispatch_response(path)
                new_emails = self.get_site_emails(html)
                if verbose:
                    for email in new_emails:
                        print('[+] Found email: ' + email)
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
    parser.add_argument('--depth', dest='depth', type=int, default=1, help='Depth of search ramifications.')
    parser.add_argument('--output', dest='output', type=str, help='The file path for the found emails.')
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    depth = args.depth + 1
    for url in args.urls:
        site = SiteBrowser(url)
        emails = site.scrap_emails(depth)
        if emails:
            print('\nFound ' + str(len(emails)) + ' emails:')
            for email in emails:
                str_line = "[+] Found email from " + site.domain + " -> " + email
                if args.print:
                    print(str_line)
    if args.output:
        with open(args.output, "w") as f:
            for url in args.urls:
                f.write(url + "\n")


if __name__ == '__main__':
    main()