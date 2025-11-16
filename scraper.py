#!/usr/bin/ python3


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
import sys
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
    return parser.parse_args()

class Scraper:
    def __init__(self, file):
        self.logger = logger()
        with open(file, 'r') as obj:
           params = json.load(obj)
        self.titles = params['titles']
        self.sites = params['sites']
        self.date = params['date']
        self.serp_api_key = params['api_keys']['serp']
       # self.gpt_api_key = params['api_key']['gpt']
        self.location = params['location']
        self.compensation = params.get('compensation')
        self.work_mode = params.get('work_mode')
        self.cities = self.location.get('cities')
        self.levels_want = params.get('levels', {}).get('seek')
        self.levels_avoid = params.get('levels', {}).get('avoid')
        self.num_results = params.get('num_results', [10] * len(self.location))

    def get_country_code(self, country):
            url = f"https://restcountries.com/v3.1/name/{country}?fullText=true&fields=cca2"
            response = requests.get(url)
            data = response.json()
            response.raise_for_status()
            return data[0]['cca2'].lower()

    def str_constructor(self, country, cities = None):
        all_sites = ['greenhouse.io', 'jobs.ashbyhq.com', 'jobs.lever.co'] # More sites to be added later!
        self.logger.info('Constructing Search String...')
        if self.sites == 'all':
            first = ' OR '.join([f'site:{site}' for site in all_sites])
        else:
            first = ' OR '.join([f'site:{site}' for site in self.sites])
        second = f'({" OR ".join("\"{}\"".format(t) for t in self.titles)})'
        third = f'after:{self.date}'
        string =  first + ' ' + second + ' ' + third
        if self.work_mode:
            string += f' ("{" OR ".join(self.work_mode)}")'
        if cities and self.work_mode != ['Remote']:
            string += f' ({" OR ".join(cities)})' 
        string += f' "{country}"' 
        if self.levels_want:
            want_q = " ".join(f'"{level}"' for level in self.levels_want)
            string += ' ' + want_q
        if self.levels_avoid:
            avoid_q = " ".join(f'-"{level}"' for level in self.levels_avoid)
            string += ' ' + avoid_q
        return string

    def google_search(self):
        df_list = []
        self.logger.info('Collecting Google Search Results...')
    
        for num, c in zip(self.num_results, self.location.keys()):
            query = {
                'engine': 'google',
                'q': self.str_constructor(c, self.location[c]),
                'location': c,
                'gl': self.get_country_code(c),
                'api_key': self.serp_api_key,
                'num': num
                    }
    
            results = GS(query).get_dict().get('organic_results', [])
            results = results[:num]  # num isn't guaranteed to work, for some reason...
            df_list.append(pd.DataFrame(results))

        df = pd.concat(df_list)
        df.drop(['redirect_link', 'displayed_link', 'favicon', 'snippet'], axis = 1, inplace = True)
        df['position'] = range(1, len(df) + 1)
        return df
    
# test out the class below

if __name__ == '__main__':
    args = args()
    obj = Scraper(args.file)
    if args.csv:
        data = obj.google_search()
        data.to_csv('output.csv', index = False)

