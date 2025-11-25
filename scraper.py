#!/usr/bin/python3

# Use SQLite to store the historical data?

import pandas as pd
import helper as hp
from dacite import from_dict

log = hp.logger()

# url = f"https://serpapi.com/searches.json?api_key={self.c.api_keys.serp}"
# url = f"https://restcountries.com/v3.1/name/{country}?fullText=true&fields=cca2"

class Scraper:
    def __init__(self, file):
        import json
        with open(file, 'r') as obj:
           params = json.load(obj)
        self.c = from_dict(hp.Config, params)
    
    def req_wrapper(self, url):
        import requests
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()
        return data
    
    def queries_left(self):
        url = f"https://serpapi.com/account?api_key={self.c.api_keys.serp}"
        stats = self.req_wrapper(url)
        print(f"You have {stats['plan_searches_left']} SerpAPI searches left.")

    def str_constructor(self, country, cities = None):
        from serpapi import GoogleSearch as GS
        all_sites = ['greenhouse.io', 'jobs.ashbyhq.com', 'jobs.lever.co'] # More sites to be added later!
        log.info('Constructing Search String...')
        if self.c.sites == 'all':
            first = '(' + ' OR '.join([f'site:{site}' for site in all_sites]) + ')'
        else:
            first = '(' + ' OR '.join([f'site:{site}' for site in self.c.sites]) + ')'
        second = '(' + ' OR '.join(f'"{title}"' for title in self.c.titles) + ')'
        third = f'after:{self.c.date}'
        string =  first + ' ' + second + ' ' + third
        if self.c.work_mode:
            string += ' (' + ' OR '.join(f'"{mode}"' for mode in self.c.work_mode) + ')'
        if cities and self.c.work_mode != ['Remote']:
            string += ' (' + ' OR '.join(f'"{city}"' for city in cities) + ')' 
        if self.c.levels.seek:
            want_q = " ".join(f'"{level}"' for level in self.c.levels.seek)
            string += ' ' + want_q
        if self.c.levels.avoid:
            avoid_q = " ".join(f'-"{level}"' for level in self.c.levels.avoid)
            string += ' ' + avoid_q
        return string
    
    def google_search(self):
        from serpapi import GoogleSearch as GS
        df_list = []
        url = "https://restcountries.com/v3.1/name/{}?fullText=true&fields=cca2"
        log.info('Collecting Google Search Results...')
    
        for num, c in zip(self.c.results_per_page, self.c.location.keys()):
            for page in range(self.c.max_pages):
                query = {
                    'engine': 'google',
                    'q': self.str_constructor(c, self.c.location[c]),
                    'location': c,
                    'gl': self.req_wrapper(url.format(c))[0]['cca2'].lower(),
                    'start': page * 10,
                    'api_key': self.c.api_keys.serp,
                    'num': num
                        }
                
                results = GS(query).get_dict().get('organic_results', [])
                results = results[:num]  # num isn't guaranteed to work, for some reason...
                df_list.append(pd.DataFrame(results))

        df = pd.concat(df_list)
        df.drop(['redirect_link', 'displayed_link', 'favicon', 'snippet'], axis = 1, inplace = True, errors = 'ignore')
        df['position'] = range(1, len(df) + 1)
        return df
    
# test out the class below

if __name__ == '__main__':
    args = hp.args()
    obj = Scraper(args.json)
    data = obj.google_search()
    if args.csv:
        data.to_csv('output.csv', index = False)
    if args.notify:
        obj.queries_left()