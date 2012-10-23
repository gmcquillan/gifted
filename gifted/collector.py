import datetime
import hashlib
import json
import os
import time

import requests

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

INTERVAL = 1800
USER_AGENT = 'Gif Search Bot by gmcquillan'


def make_dir(path):
    if path and not os.access(path, os.R_OK):
        return os.mkdir(path)


class Collector(object):
    parent_data_dir = 'data'

    def __init__(self):
        make_dir(self.parent_data_dir)

    def make_soup(self, url):
        headers = {'User-Agent': USER_AGENT}
        return BeautifulSoup(requests.get(url, headers=headers).content)

    def extract_gif_urls(self, soup):
        gif_urls = []
        for link in soup.find_all('a'):
            href = link.attrs.get('href')
            if href and href.find('.gif') > -1:
                gif_urls.append(href)

        return gif_urls

    def extract_next_urls(self, soup):
        next_urls = []
        for link in soup.find_all('a'):
            if link.contents and link.contents == [u'next \u203a']:
                next_urls.append(link.attrs['href'])

        return next_urls

    def md5_is_on_disk(self, md5):
        return md5 + '.gif' in os.listdir(
            self.parent_data_dir
        )

    def download_gifs(self, gif_urls):
        tag_dir = 'data/tags'
        if not os.path.exists(tag_dir):
            os.mkdir(tag_dir)

        for gif_url in gif_urls:
            if gif_url.startswith('https'):
                gif_url.replace('https://', 'http://')
            gif = requests.get(gif_url)
            md5 = hashlib.md5(gif.content).hexdigest()
            if self.md5_is_on_disk(md5):
                continue
            filename = md5 + '.gif'
            with open('/'.join(
                [self.parent_data_dir, filename]
            ), 'w') as f:
                f.write(gif.content)

            if not os.path.exists(
                '{tag_dir}/{filename}.json'.format(
                    tag_dir=tag_dir,
                    filename=filename
                )
            ):
                with open(
                    'data/tags/{filename}.json'.format(filename=filename), 'w'
                ) as f:
                    f.write(
                        json.dumps(
                            {
                                'data': [],
                                'meta': {
                                    'content-length': int(
                                        gif.headers.get('content-length')
                                    )
                                }
                            }
                        )
                    )

    def process(self):
        """This function must be overridden."""
        pass


class RedditCollector(Collector):

    def __init__(self):
        super(RedditCollector, self).__init__()
        make_dir(self.parent_data_dir)

    def process(self, num=10):
        count = 0
        for run in range(0, num):
            if count < 1:
                soup = self.make_soup('http://www.reddit.com/r/gifs')
            url = self.extract_next_urls(soup)[-1]
            if url:
                soup = self.make_soup(url)
            self.download_gifs(
                self.extract_gif_urls(soup)
            )
            count += 1
            time.sleep(0.01)


def do_process_collectors(collectors):
    for collector in collectors:
        collector.process()


def process_collectors(collectors, interval=INTERVAL):
    now = datetime.datetime.now()
    next_run = now + relativedelta(seconds=+interval)
    do_process_collectors(collectors)
    while 1:
        now = datetime.datetime.now()
        if now < next_run:
            time.sleep(0.5)
            continue
        do_process_collectors(collectors)
        next_run = now + relativedelta(seconds=+interval)


def main():
    collector = RedditCollector()
    process_collectors([collector])


if __name__ == '__main__':
    main()
