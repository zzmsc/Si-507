# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 23:47:20 2023

@author: zzmsc
"""

import csv
from os.path import exists
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from PIL import Image
from io import BytesIO
import json

def crawl_data():
    headers = {# camouflage as browser
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    search_query = 'jacket'.replace(' ', '+')
    base_url = 'https://www.amazon.com/s?k={0}'.format(search_query)

    items = []
    for i in range(1, 10):
        print('Processing {0}...'.format(base_url + '&page={0}'.format(i)))
        response = requests.get(base_url + '&page={0}'.format(i), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        for result in results:
            product_name = result.h2.text

            try:
                rating = result.find('i', {'class': 'a-icon'}).text
                rating_count = result.find_all('span', {'aria-label': True})[1].text
            except AttributeError:
                continue

            try:
                price1 = result.find('span', {'class': 'a-price-whole'}).text
                price2 = result.find('span', {'class': 'a-price-fraction'}).text
                price = float(price1 + price2)
                product_url = 'https://amazon.com' + result.h2.a['href']
                # print(rating_count, product_url)
                items.append([product_name, rating, rating_count, price, product_url])
            except AttributeError:
                continue
        sleep(1.5)
        
    df = pd.DataFrame(items, columns=['product', 'rating', 'rating count', 'price', 'product url'])
    df.to_csv('{0}.csv'.format(search_query), index=False)
    
def crawl_pic(url):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('div', {'class': 'imgTagWrapper'})
    img_tag = results[0].find('img')
    first_url = img_tag['src']
    response = requests.get(first_url, headers=headers)
    img = Image.open(BytesIO(response.content))
    img.show()

def open_file(file):
    '''
        Funciton that used for open csv file, which is also the cache file
    '''
    with open(file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows



def store_source(rows):
    ''' Function that organize all data source and remove the duplicated data
    
    Parameters
    ----------
    rows: list
        a list of dictionaies that contains all product information including price, rating,
    rating count and product url
    
    Returns
    -------
    all_product: list
        list of all unique product name
    '''
    all_product=[]
    for item in rows:
        all_product.append(item['product'])
    all_product = list(set(all_product))
    return all_product




def usageTree(rest_tree,type):
    ''' Function that organize the tree into a dictionary contains usage level information
    
    Parameters
    ----------
    rows: list
        a list of dictionaies that contains all product information including price, rating,
    rating count and product url
    
    Returns
    -------
    usagecountTree['rate']: list
        priceTree is a dictionary that contains the all rate information with key "price"
    len(usageTree['count']): int
        The length of usage list
    '''
    usageTree = {'use': []}
    for use in rest_tree:
        try:
            if type.lower() in use['product'].lower():
                usageTree['use'].append(use['product'])
        except:
            pass

    return usageTree['use'], len(usageTree['use'])


def ratingcountTree(rest_tree, min=0, max=5000):
    ''' Function that organize the tree into a dictionary contains rating count level information
    
    Parameters
    ----------
    rows: list
        a list of dictionaies that contains all product information including price, rating,
    rating count and product url
    
    Returns
    -------
    ratingcountTree['rate']: list
        priceTree is a dictionary that contains the all rate information with key "price"
    len(ratingcountTree['count']): int
        The length of rating count list
    '''
    ratingcountTree = {'count': []}
    for count in rest_tree:
        try:
            if min <= float(count["rating count"]) <= max:
                ratingcountTree['count'].append(count['product'])
        except:
            pass

    return ratingcountTree['count'], len(ratingcountTree['count'])


def priceTree(rest_tree, min=0, max=200):
    
    ''' Function that organize the tree into a dictionary contains price level information
    
    Parameters
    ----------
    rows: list
        a list of dictionaies that contains all product information including price, rating,
    rating count and product url
    
    Returns
    -------
    priceTree['rate']: list
        priceTree is a dictionary that contains the all rate information with key "price"
    len(priceTree['price']): int
        The length of price list
    '''
    
    priceTree = {'price': []}
    for price in rest_tree:
        try:
            if min <= float(price["price"]) <= max:
                priceTree['price'].append(price['product'])
        except:
            pass

    return priceTree['price'], len(priceTree['price'])

def rateTree(rest_tree, min=0, max=5):
    
    ''' Function that organize the tree into a dictionary contains rating level information
    
    Parameters
    ----------
    rows: list
        a list of dictionaies that contains all product information including price, rating,
    rating count and product url
    
    Returns
    -------

    rateTree['rate']: list
        rateTree is a dictionary that contains the all rate information with key "rate"

    len(rateTree['rate']): int
        The length of rating list
    '''

    rateTree = {'rate': []}
    for rate in rest_tree:
        try:
            if min <= float(rate["rating"][0:3]) <= max:
                rateTree['rate'].append(rate['product'])
        except:
            pass
    return rateTree['rate'], len(rateTree['rate'])

def intersection(use, price, rating, count):
    target = set(use) & set(price) & set(rating) & set(count)
    return list(target), len(list(target))

def store_information(target, rows):
    price = []
    rate = []
    count = []
    for item in rows:
        for i in range(len(target)):
            if item['product'] == target[i]:
                try:
                    price.append({'product':item['product'],"price":float(item["price"])})
                    rate.append({'product':item['product'],"rate":float(item["rating"][0:3])})
                    count.append({'product':item['product'],"count":int(item["rating count"])})
                except:
                    pass

    return price, rate, count

def priority_choice(price_least=0, price_most=0, count_least=0, count_most=0, rate_least=0, rate_most=0, price_info=[], rate_info=[], count_info=[]):
    final_suggestion=[]
    if price_least:
        final_suggestion = price_info[0]
        for item in price_info:
            if item['price'] < final_suggestion['price']:
                final_suggestion = item
    elif price_most:
        final_suggestion = price_info[0]
        for item in price_info:
            if item['price'] > final_suggestion['price']:
                final_suggestion = item
    elif count_least:
        final_suggestion = count_info[0]
        for item in count_info:
            if item['count'] < final_suggestion['count']:
                final_suggestion = item
    elif count_most:
        final_suggestion = count_info[0]
        for item in count_info:
            if item['count'] > final_suggestion['count']:
                final_suggestion = item
    elif rate_least:
        final_suggestion = rate_info[0]
        for item in rate_info:
            if item['rate'] < final_suggestion['rate']:
                final_suggestion = item
    elif rate_most:
        final_suggestion = rate_info[0]
        for item in rate_info:
            if item['rate'] > final_suggestion['rate']:
                final_suggestion = item

    return final_suggestion

def yes(prompt):
    """Decode user's input. Prompt user a yes/no question. Return user's answer."""
    while True:
        answer = input(prompt)
        if answer.lower() == "yes":
            return True
        elif answer.lower() == "no":
            return False
        else:
            print("Please answer yes or no.")

def get_use_input(rows):
    print("The typical search key word include: Men's, Women's, kids, and so on")
    use = input('what type of jacket would you want? ')
    use_search, use_count = usageTree(rows, use)
    if use_count ==0:
        print("There is no information of what you want, please try another one")
        get_use_input(rows)
    else:
        print(f"There are {use_count} choices")
    return use_search, use_count

def get_price_input(rows):
    print("The typical price range is 0 ~ 500")
    try:
        least_price = int(input('What is the lowest price you accept? '))
        most_price = int(input('What is the highest price you accept? '))
    except:
        least_price = 0
        most_price = 500
    price_search, price_cout = priceTree(rows, min=least_price, max=most_price)
    return price_search, price_cout

def get_rate_input(rows):
    print("The typical rate range is 0 ~ 5")
    try:
        least_rate = int(input('What is the lowest rate you accept? '))
    except:
        least_rate = 0
    rate_search, rate_cout = rateTree(rows, min=least_rate, max=5)
    return rate_search, rate_cout

def get_counts_input(rows):
    print("The typical rating count range is 0 ~ 200000")
    try:
        least_count = int(input('What is the lowest count you accept? '))
    except:
        least_count = 0
    count_search, count_cout = ratingcountTree(rows, min=least_count)
    return count_search, count_cout

def get_priority_input():
    '''Function that used for get priority input
    Returns
    -------
    priority: str (should be 'price_least', if input is illegal)

    '''
    priority = input('What is your top priority?(default: price_least)  ')
    list = ['price_least', 'price_most', 'count_least', 'count_most', 'rate_least', 'rate_most']
    if priority  in list:
        return priority
    else:
        return "price_least"

file_exists = exists("jacket_data.csv")
use_backupfile = False
if use_backupfile:
    rows = open_file('jacket_data.csv')
elif not file_exists:
    crawl_data()
    rows = open_file('jacket_data.csv')
else:
    rows = open_file('jacket_data.csv')
all_product = store_source(rows)
print('Welcome to find your best jacket')
if yes("Shall we begin search? "):
    use_search, use_count = get_use_input(rows)
    price_search, price_cout = get_price_input(rows)
    rate_search, rate_count = get_rate_input(rows)
    count_search, count_count = get_counts_input(rows)
    target, target_len = intersection(use=use_search, price=price_search, rating=rate_search, count=count_search)
    if target_len == 0:
        print("There is no match, please restart with different requirement")
    elif target_len == 1:
        print(f'There is exactly 1 product that meets all your require')
        for item in rows:
            if item['product'] == target[0]:
                url = item['product url']
        final_product = target[0]
        print(f"Your final suggestion is {final_product}")
        print(f"The link of the product is {url}")
        crawl_pic(url)
    else:
        print(f"There are {target_len} matches that meet all your require")
        price_info, rate_info, count_info = store_information(target, rows)
        print("Please give me your top priority to get final result")
        print("You can choose price_least, price_most, count_least, count_most, rate_least or rate_most")
        priority = get_priority_input()
        list = ['price_least', 'price_most', 'count_least', 'count_most', 'rate_least', 'rate_most']
        final_suggestion = priority_choice(price_least=(priority==list[0]),
        price_most=(priority==list[1]),
        count_least=(priority==list[2]),
        count_most=(priority==list[3]),
        rate_least=(priority==list[4]),
        rate_most=(priority==list[5]),
        price_info=price_info, rate_info=rate_info, count_info=count_info)
        final_product = final_suggestion['product']
        print(f"Your final suggestion is {final_product}")
        for item in rows:
            if item['product'] == final_suggestion['product']:
                url = item['product url']
        print(f"The link of the product is {url}")
        crawl_pic(url)
else:
    print("bye")    
    