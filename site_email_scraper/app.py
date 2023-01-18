import re
import requests
import urllib
from bs4 import BeautifulSoup
from html import unescape

DEFAULT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'

class site_browser:
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

    def get_emails(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@'+self.domain
        return re.findall(email_pattern, text)

    def scrap_emails(self, depth):
        html = unescape(self.session.get(self.url).text)
        soup = BeautifulSoup(html, 'html.parser')
        self.emails = list(set(self.get_emails(html)))
        new_paths = [link.get('href') for link in soup.find_all('a') if self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc)]
        old_paths = []
        while depth != 0:
            paths = new_paths
            new_paths = []
            for path in paths:
                print(path)
                old_paths.append(path)
                path_html = self.session.get(path).text
                soup = BeautifulSoup(path_html, 'html.parser')
                self.emails = self.emails + self.get_emails(path_html)
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if (self.domain in str(urllib.parse.urlparse(href, scheme='', allow_fragments=True).netloc)) and (href not in old_paths):
                        new_paths.append(href)
            depth = depth - 1
        return list(set(self.emails))

    #def get_site_links():

def main():

if __name__ == '__main__':
    main()
