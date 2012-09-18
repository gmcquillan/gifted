import os
import uuid

import reddit
import requests

from bs4 import BeautifulSoup

def read_line(path):
    """Return the first line from a file."""
    with open(path, 'r') as f:
        lines = f.readlines()
        if len(lines) < 0:
            return ''
        return lines[0]

def get_password():
    return read_line('../.password')

def get_username():
    return read_line('../.username')

def make_dir(path, mode='0755'):
    if path and not os.access(path, os.R_OK):
        return os.mkdir(path, mode)


class Collector(object):
    parent_data_dir = 'data'

    def __init__(self):
        make_dir(self.parent_data_dir)


class RedditCollector(Collector):
    data_dir = 'reddit'

    def __init__(self):
        super(RedditCollector, self).__init__(self)
        make_dir('/'.join([self.parent_data_dir, self.data_dir]))
        self.user = get_username()
        self.password = get_password()
        self.r = reddit.Reddit(user_agent='Gif Search Bot by gmcquillan')
        self.r.login(username=self.username, password=self.password)


    def get_story_urls(self, sub_reddit='gif', **kwargs):
        sub = self.r.get_subreddit(sub_reddit)
        commands = kwargs.get('commands')
        raw_sub_results = []
        if not commands:
            raw_sub_results = sub.get_new()
        else:
            # If we want to pull from multiple sorted sets:
            # e.g.: new, top_from_year, hot, etc.
            for command in commands:
                try:
                    raw_sub_results.append(
                        sub.getattr(command)()
                    )
                except Exception:
                    pass

        return [item.url for item in raw_sub_results]

    def extract_gif_urls(self, story_urls):
        gif_urls = []
        for url in story_urls:
            soup = BeautifulSoup(requests.get(url).content)
            for link in soup.find_all('a'):
                href = link.attrs.get('href')
                if href and href.find('.gif') > -1:
                    gif_urls.append(href)

        return gif_urls

    def make_file_name(self, suffix='gif'):
        return '.'.join([str(uuid.uuid4()).replace('-', ''), suffix])

    def download_gifs(self, gif_urls):
        for gif_url in gif_urls:
            gif = requests.get(gif_url)
            with open(self.make_file_name, 'w') as f:
                f.write(gif.content)
