import re
import requests
import urllib
from bs4 import BeautifulSoup
from html import unescape
import argparse


DEFAULT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'


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
        with open('web.html', 'w') as f:
            f.write(text)
        email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        return list(set(re.findall(email_pattern, text)))

    def get_site_paths(self, soup):
        return (link.get('href') for link in soup.find_all('a') if self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc))

    def scrap_emails(self, depth):
        html, soup = self.dispatch_response(self.url)
        self.emails = self.get_site_emails(html)
        visited_paths = {self.url}
        next_paths = self.get_site_paths(soup)
        while depth > 0:
            paths = next_paths
            next_paths = []
            for path in paths:
                visited_paths.add(path)
                html, soup = self.dispatch_response(path)
                self.emails += self.get_site_emails(html)
                for link in set(self.get_site_paths(soup)): # will have to make it so it excludes images
                    if link not in visited_paths:
                        next_paths.append(link)
            depth = depth - 1
        return list(set(self.emails))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('urls', metavar='URL', type=str, nargs='+', help='A list of one or more URLs')
    parser.add_argument('--print', dest='print', action='store_true', help='Print the URLs')
    parser.add_argument('--depth', dest='depth', type=int, default=1, help='Depth of search ramifications.')
    parser.add_argument('--output', dest='output', type=str, help='The file path for the found emails.')
    args = parser.parse_args()
    for url in args.urls:
        site = SiteBrowser(url)
        emails = site.scrap_emails(args.depth)
        for email in emails:
            str_line = "[+] Found email from " + site.domain + " : " + email
            if args.print:
                print(str_line)
    if args.output:
        with open(args.output, "w") as f:
            for url in args.urls:
                f.write(url + "\n")


if __name__ == '__main__':
    main()