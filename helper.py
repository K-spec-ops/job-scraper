import argparse
import logging
from dataclasses import dataclass, field
from typing import Union
# helper file for scraper

@dataclass
class Levels:
    seek: list[str]
    avoid: list[str]

@dataclass
class APIKeys:
    serp: str
    gpt: str

@dataclass
class Config:
    api_keys: APIKeys
    levels: Levels
    location: dict[str, list[str]]
    titles: list[str]
    date: str
    max_pages: int = 3
    compensation: int = None
    sites: Union[str, list[str]] = 'all'
    work_mode: list[str] = field(default_factory = list)
    results_per_page: list[int] = field(default_factory = list)

    def __post_init__(self):
        if not self.results_per_page:
            self.results_per_page = [10] * len(self.location)

def logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

def args():
    parser = argparse.ArgumentParser(prog = 'scraper.py', description = 'Python script to scrape job boards and automate the application process.')
    parser.add_argument('json', help = 'Specify a .json file containing the search parameters.', action = 'store')
    parser.add_argument('-c', '--csv', help = 'Generate a .csv file of the scraped data.', action = 'store_true', required = False)
    parser.add_argument('-t', '--track', help = 'Track applications made using this script.', action = 'store_true', required = False)
    parser.add_argument('-n', '--notify', help = 'Print a message to the console with the number of serpapi searches left.', action = 'store_true', required = False)
    return parser.parse_args()