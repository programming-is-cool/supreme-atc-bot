from utils import get_params, product_link, checkout
import requests
from bs4 import BeautifulSoup
import time
import random

from selenium.webdriver import ChromeOptions
from selenium import webdriver
from termcolor import colored


# Categories of the items you want.

categories = [
    't-shirts',
    'accessories',
    'tops/sweaters'
]

# ----------------------------------------------------------------------

# example = [
#     ['82L' 'red']
# ]

keywords = [
    ['hanes', 'white'],
    ['hanes']
]

# ----------------------------------------------------------------------

# Size you want if a size is required.
sizes = [
    'Small',
    'Medium',
    'S',
    'SM',
    'M',
    'MD'
]

delay = 2

# ----------------------------------------------------------------------

# Checkout information.

checkout_values1 = {
        'billing_name': 'John Doe',
        'email': 'example@example.com',
        'tel': '321 554 1234',
        'billing_address': '123 Main St',
        #'billing_address2': '3E',
        'billing_zip': '10002',
        'billing_city': 'New York',
        'order_billing_state': 'NY',
        'credit_card[nlb]': '4207 6702 0000 1111',
        'credit_card[rvv]': '283',
        'credit_card_month': '01',
        'credit_card_year': '2021'
    }

# ----------------------------------------------------------------------


def main():
    global list_of_urls, found_category
    successful_post = 0
    driver = webdriver.Firefox()

    with requests.Session() as s:

        driver.get('https://www.supremenewyork.com/shop/all')

        print(input('Hit enter to start task:'))

        script_start = time.time()

        header = {
            'Host': 'www.supremenewyork.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        for cookie in driver.get_cookies():
            c = {cookie['name']: cookie['value']}
        s.cookies.update(c)

        while True:
            time.sleep(round(random.uniform(0.2, 1.0), 2))
            for category in categories:
                html = s.get('https://supremenewyork.com/shop/all/{}'.format(category), headers=header)
                html_doc = BeautifulSoup(html.content, 'html.parser')
                print(colored('********  Searching through "{}"  ********'.format(category), 'cyan'))
                list_of_urls = product_link(html_doc, keywords)
                if list_of_urls:
                    found_category = category
                    break
            else:
                print(colored("Couldn't find the product in any of the categories provided.", 'red'))
                print(colored('Reloading...', 'green'))
            if list_of_urls:
                break

        for url in list_of_urls:
            header = {
                'Host': 'www.supremenewyork.com',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': url,
                'X-XHR-Referer': 'http://supremenewyork.com/shop/all/{}'.format(found_category)
            }
            page = s.get(url, headers=header)
            product_page = BeautifulSoup(page.content, 'html.parser')
            post_params = get_params(product_page_html=product_page, wanted_sizes=sizes)
            if post_params:
                post_url = product_page.find(class_='add')
                header = {
                    'Host': 'www.supremenewyork.com',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
                    'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, '
                              'application/x-ecmascript',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': url
                }
                s.post('https://www.supremenewyork.com{}'.format(post_url['action']), data=post_params, headers=header)
                successful_post += 1
            else:
                print(colored('Item is sold out!', 'red'))
        if successful_post > 0:
            for cookie in s.cookies:
                driver.add_cookie({
                    'name': cookie.name,
                    'value': cookie.value,
                    'path': '/',
                })
            driver.get('https://www.supremenewyork.com/checkout')
            print(colored('********  On checkout page!  ********', 'cyan'))
            checkout_page_time = time.time()
            print(colored('Time it took for script to reach checkout: {} seconds'.format(
                round(checkout_page_time - script_start, 2)), 'yellow'))

            checkout(driver, checkout_values1, script_start, delay)
        else:
            print('No items were added to the cart.')


if __name__ == '__main__':
    main()
