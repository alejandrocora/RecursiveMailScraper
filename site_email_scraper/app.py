import re
import requests
import urllib
from bs4 import BeautifulSoup
from html import unescape

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
        email_pattern = r'[a-zA-Z0-9._%+-]+@'+self.domain
        return list(set(re.findall(email_pattern, text)))

    def get_site_paths(self, soup):
        return (link.get('href') for link in soup.find_all('a') if self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc))

    def scrap_emails(self, depth):
        html, soup = self.dispatch_response(self.url)
        self.emails = self.get_site_emails(html)
        new_paths = self.get_site_paths(soup)
        old_paths = [self.url]
        while depth > 0:
            paths = list(set([path for path in new_paths if path not in old_paths]))
            new_paths = []
            for path in paths:
                html, soup = self.dispatch_response(path)
                self.emails = self.emails + self.get_site_emails(html)
                for link in self.get_site_paths(soup):
                    if link not in old_paths:
                        new_paths.append(link)
                old_paths.append(path)
            old_paths = list(set(old_paths))
            depth = depth - 1
        return list(set(self.emails))

def main():
    a = SiteBrowser('https://google.com/')
    print(a.scrap_emails(0))

if __name__ == '__main__':
    main()
