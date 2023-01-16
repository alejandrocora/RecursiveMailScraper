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

    def get_emails(text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, text)

    def scrap_emails(self, depth):
        html = unescape(self.session.get(self.url).text)
        soup = BeautifulSoup(html, 'html.parser')
        self.emails = self.emails + list(set(site_browser.get_emails(html)))
        links = soup.find_all('a')
        paths = [urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).path for link in links if self.domain in str(urllib.parse.urlparse(link.get('href'), scheme='', allow_fragments=True).netloc)]
        new_paths = []
        while depth != 0:
            for link in links:
                self.emails = self.emails + site_browser.get_emails(self.session.get(link))


    #def get_site_links():

    #list(set(list))

def main():
    new_site = site_browser('https://tictour.com/')
    html = new_site.scrap_emails(1)

if __name__ == '__main__':
    main()