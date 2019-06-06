import re
import time

from selenium.webdriver.support.ui import Select
from termcolor import colored


def product_link(page_html, product_list):
    """
    Accepts an HTML object of the category page and returns a list of the url's
    for each product in the product list

    :param page_html: HTML of category page.
    :param product_list: List element of product name and color. Example: ['Zippo Lighter', 'Red']
    :return: URL of the product
    """

    url_link_list = []
    for article in page_html.find_all('article'):
        if len(product_list) > 0:
            for product in product_list:
                if len(product) == 2:
                    if re.search(r'\b' + product[0] + r'\b', str(article.h1.a.text), flags=re.IGNORECASE) and \
                            re.search(r'\b' + product[1] + r'\b', str(article.p.a.text), flags=re.IGNORECASE):
                        link = article.h1.a['href']
                        item_link = 'http://supremenewyork.com{}'.format(link)
                        print(colored('Found "{}".'.format(article.h1.a.text), 'green'))
                        url_link_list.append(item_link)
                    else:
                        print(colored("Couldn't locate the item. Found '{}' instead.".format(article.h1.a.text), 'red'))

                elif len(product) == 1:
                    if re.search(r'\b' + product[0] + r'\b', str(article.h1.a.text), flags=re.IGNORECASE):

                        link = article.h1.a['href']
                        item_link = 'http://supremenewyork.com{}'.format(link)
                        print(colored('Found "{}".'.format(article.h1.a.text), 'green'))
                        url_link_list.append(item_link)
                    else:
                        print(colored("Couldn't locate the item. Found '{}' instead.".format(article.h1.a.text), 'red'))
        else:
            break
    return url_link_list


def get_params(product_page_html, wanted_sizes):

    params = {}

    if product_page_html.find(class_='add'):
        for names in product_page_html.find_all('input'):
            param = names['name']
            values = names['value']
            params[param] = values

        # if product requires a size, it will add the size large to the request parameters
        if product_page_html.find_all('select', id='s'):
            param = product_page_html.find('select', id='s')['id']
            for sizes in product_page_html.find_all('option'):
                if sizes.text in wanted_sizes:
                    print(colored('Found size "{}".'.format(sizes.text), 'green'))
                    values = sizes['value']
                    params[param] = values
                    return params
        else:
            return params
    else:
        return None


def checkout(web_driver, payment_info, start_time, delay):

    web_driver.find_element_by_id("order_billing_name").send_keys(payment_info['billing_name'])
    web_driver.find_element_by_id("order_email").send_keys(payment_info['email'])
    web_driver.find_element_by_id("order_tel").send_keys(payment_info['tel'])
    web_driver.find_element_by_id("bo").send_keys(payment_info['billing_address'])

    # Checks if an apartment number is used.  If False, it will skip that field.
    try:
        web_driver.find_element_by_id("oba3").send_keys(payment_info['billing_address2'])
    except KeyError:
        pass

    web_driver.find_element_by_id("order_billing_zip").send_keys(payment_info['billing_zip'])
    web_driver.find_element_by_id("order_billing_city").send_keys(payment_info['billing_city'])
    Select(web_driver.find_element_by_id("order_billing_state")).select_by_visible_text(payment_info['order_billing_state'])
    web_driver.find_element_by_name("credit_card[nlb]").send_keys(payment_info['credit_card[nlb]'])
    web_driver.find_element_by_name("credit_card[rvv]").send_keys(payment_info['credit_card[rvv]'])
    web_driver.find_element_by_xpath(
        "//select[@id='credit_card_month']/option[@value=" + payment_info['credit_card_month'] + "]").click()
    web_driver.find_element_by_xpath(
        "//select[@id='credit_card_year']/option[@value=" + payment_info['credit_card_year'] + "]").click()
    click_box = web_driver.find_elements_by_class_name('iCheck-helper')
    for index in range(0, len(click_box)):
        if index == 1:
            click_box[index].click()

    delay_checkpoint = time.time()

    if round(delay_checkpoint - start_time, 2) < delay:
        print(colored('Delaying checkout....', 'cyan'))
        time.sleep(delay - round(delay_checkpoint - start_time, 2))

    web_driver.find_element_by_xpath("//input[@name='commit']").click()
    end_script = time.time()
    print(
        colored('Time it took for script to complete: {} seconds'.format(round(end_script - start_time, 2)), 'yellow'))