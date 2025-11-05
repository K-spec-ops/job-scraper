#!/usr/bin/env python3


# Scrape all the job websites

# We want to get a dataframe containing:
#   - Job title
#   - Company title
#   - Compensation
#   - URL
#   - ChatGPT description of the qualifications needed
#   - Years of experience needed?

# Use SQLite to store the historical data?

import requests
import argparse
import logging
import sqlite3
import pandas as pd
import json
from serpapi import GoogleSearch as GS

pd.set_option('display.max_columns', None)

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
    parser.add_argument('-f', '--file', help = 'Specify a .json file containing the search parameters.', required = True, metavar = 'JSON')
    parser.add_argument('-c', '--csv', help = 'Generate a .csv file of the scraped data.', action = 'store_true', required = False)
    parser.parse_args()
    return parser

api_key = "0432d3f23664d17e7b661aae26d63f02e6b11f41f162883fbd3717c1150075ba"

# params = {

#    "engine": "google",
#    "q": "site:greenhouse.io intitle:'data analyst' after:2025-10-01 -senior",
#    "gl": "us",
#    "num": 5,
#   "api_key": api_key

#}

#search = GS(params)
#results = search.get_dict()

#print(results['organic_results'][0]['snippet'])
#with open('results.json', 'w') as outfile:
#    logger.info('Writing results to results.json')
#    json.dump(results, outfile, )
#print(results['organic_results'])

#df = pd.DataFrame(results['organic_results'])
# Get the first 6 column names and select them
#print(df.iloc[:, :3])
#print(df[df.columns[:6]])

# for result in results['organic_results']:

class Scraper:
    def __init__(self, params):
        self.logger = logger()
        self.titles = params['titles']
        self.sites = params['sites']
        self.date = params['date']
        self.api_key = params['api_key']
        self.work_mode = params.get('work_mode')
        self.country = params.get('location', {}).get('country')
        self.cities = params.get('location', {}).get('cities')
        self.levels_want = params.get('levels', {}).get('seek')
        self.levels_avoid = params.get('levels', {}).get('avoid')
        self.num_results = params.get('num_results', 10)

    def str_constructor(self):
        all_sites = ['greenhouse.io', 'jobs.ashbyhq.com', 'jobs.lever.co'] # More sites to be added later!
        self.logger.info('Constructing Search String...')
        if self.sites == 'all':
            first = ' OR '.join([f'site:{site}' for site in all_sites])
        else:
            first = ' OR '.join([f'site:{site}' for site in self.sites])
        second = f'("{" OR ".join(self.titles)}")'
        third = f'after:{self.date}'
        query =  first + ' ' + second + ' ' + third
        if self.work_mode:
            query += f' ("{" OR ".join(self.work_mode)}")'
        if self.cities and not self.work_mode != ['Remote']:
            query += f' ("{" OR ".join(self.cities)}")'
        if self.levels_want:
            want_q = " ".join(f'"{level}"' for level in self.levels_want)
            query += ' ' + want_q
        if self.levels_avoid:
            avoid_q = " ".join(f'-"{level}"' for level in self.levels_avoid)
            query += ' ' + avoid_q

        return query

    def google_search(self):
        self.logger.info('Collecting Google Search Results...')
        pass

# test out the class below

if __name__ == '__main__':
   # args = args()
    params = {'titles': ['data analyst', 'data scientist'], 'sites': 'all', 'date': '2025-10-01', 'location': {'country': 'US', 'cities': ['San Francisco', 'New York']},
          'levels': {'seek': ['senior'], 'avoid': ['principal']}, 'num_results': 5, 'api_key': api_key}
    obj = Scraper(params)
    print(obj.str_constructor())

