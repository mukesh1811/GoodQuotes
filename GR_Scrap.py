import argparse
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import csv
import os
import time


def compile_url(tag, page):
    return f'https://www.goodreads.com/quotes/tag/{tag}?page={page}'

def get_soup(url):
    response = urlopen(Request(url))
    return BeautifulSoup(response, 'html.parser')

def extract_quotes_elements_from_soup(soup):
    elements_quotes = soup.find_all("div", {"class": "quote mediumText"})
    return elements_quotes

def extract_quote(quote_element):
    try:
        quote = quote_element.find('div', {'class': 'quoteText'}).get_text("|", strip=True)
        # first element is always the quote
        quote = quote.split('|')[0]
        quote = re.sub('^“', '', quote)
        quote = re.sub('”\s?$', '', quote)
        return quote
    except:
        return None

def extract_author(quote_element):
    try:
        author = quote_element.find('span', {'class': 'authorOrTitle'}).get_text()
        author = author.strip()
        author = author.rstrip(',')
        return author
    except:
        return None

def extract_source(quote_element):
    try:
        source = quote_element.find('a', {'class': 'authorOrTitle'}).get_text()
        return source
    except:
        return None

def extract_tags(quote_element):
    try:
        tags = quote_element.find('div', {'class': 'greyText smallText left'}).get_text(strip=True)
        tags = re.sub('^tags:', '', tags)
        tags = tags.split(',')
        return tags
    except:
        return None

def extract_likes(quote_element):
    try:
        likes = quote_element.find('a', {'class': 'smallText', 'title': 'View this quote'}).get_text(strip=True)
        likes = re.sub('likes$', '', likes)
        likes = likes.strip()
        return int(likes)
    except:
        return None

def extract_quote_dict(quote_element):
    quote_data = {'quote': extract_quote(quote_element),
                          'author': extract_author(quote_element),
                          'source': extract_source(quote_element),
                          'likes': extract_likes(quote_element),
                          'tags': extract_tags(quote_element)}

    return quote_data

def download_quotes_from_page(tag, page):
    url = compile_url(tag, page)
    print(f'Retrieving {url}...')
    
    try:
        soup = get_soup(url)
        quote_elements = extract_quotes_elements_from_soup(soup)
        return [extract_quote_dict(e) for e in quote_elements]
    except Exception as e:
        print(str(e))
        return ""

def download_all_pages(tag, max_pages, max_quotes):
    results = []
    p = 1
    while p <= max_pages:
        time.sleep(1)
        res = download_quotes_from_page(tag, p)
        if len(res) == 0:
            print(f'No results found on page {p}.\nTerminating search.')
            return results

        results = results + res

        if len(results) >= max_quotes:
            print(f'Hit quote maximum ({max_quotes}) on page {p}.\nDiscontinuing search.')
            return results[0:max_quotes]
        else:
            p += 1

    return results

def download_goodreads_quotes(tag, max_pages=1, max_quotes=50):
    return download_all_pages(tag, max_pages, max_quotes)

def recreate_quote(dict):
    return f'"{dict.get("quote")}" - {dict.get("author")}'

def save_quotes(quote_data, tag):
    save_path = os.path.join(os.getcwd(), 'scraped' + '-' + tag + '.txt')
    print('saving file')
    with open(save_path, 'w', encoding='utf-8') as f:
        quotes = [recreate_quote(q) for q in quote_data]
        for q in quotes:
            f.write(q + '\n')




tag = 'relationship'

mp = 100

mq = mp * 30
#mq = 1

results = download_goodreads_quotes(tag, max_pages=mp, max_quotes=mq)

tag_set = set()
tag_list = list()


for result in results:
    for tag in result['tags']:
        tag_set.add(tag)
        tag_list.append(tag)


print("results len")
print(len(results))
print("tags list len")
print(len(tag_list))
print("tags set len")
print(len(tag_set))

import pandas as pd

pd.DataFrame(list(tag_set),columns=['Tags']).to_csv("tags.csv",index=False)

import datetime as dt
print(dt.datetime.now())