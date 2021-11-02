from io import TextIOWrapper
from PyInquirer import prompt
from examples import custom_style_3
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import pyperclip
import time

METAMASK_EXTENSION = './extensions/Metamask.crx'
CHROME_DRIVER = './drivers/chromedriver'
META_START_URL = 'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#initialize/create-password/import-with-seed-phrase'
NEW_PASSWORD = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
RECOVERY_PHRASE = ''
NFTSEA_URL = 'https://nftsea.net/'
ADDRESSES = []


def create_wallets(browser: WebDriver, eth_address: str):

    browser.get(META_START_URL)
    wait = WebDriverWait(browser, 1000)
    isFirst = True
    hadError = False
    phrase = RECOVERY_PHRASE

    print(f'Parsing for [{phrase}]')

    text_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[class$="__seedphrase"] input'))
    )
    text_field.send_keys(phrase)

    browser.find_element_by_id('password').send_keys(NEW_PASSWORD)

    browser.find_element_by_id('confirm-password').send_keys(NEW_PASSWORD)

    if isFirst:
        browser.find_element_by_class_name(
            'first-time-flow__terms').click()

    try:
        WebDriverWait(browser, 1).until(
            EC.element_to_be_clickable((By.TAG_NAME, 'button'))).click()
    except:
        browser.refresh()
        isFirst = False
        hadError = True
        return

    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.end-of-flow button'))).click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'header.popover-header button'))).click()

    balance = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "currency-display-component__text"))
    ).text

    browser.find_element_by_css_selector(
        'button.selected-account__clickable').click()

    address = pyperclip.paste()
    ADDRESSES.append(address)

    for x in range(51):
        browser.find_element_by_css_selector(
            'div.identicon__address-wrapper').click()
        browser.find_element_by_css_selector(
            '#app-content > div > div.account-menu > div:nth-child(6)').click()
        browser.find_element_by_css_selector(
            '#app-content > div > div.main-container-wrapper > div > div > div > div:nth-child(2) > div > button.button.btn-secondary.btn--large.new-account-create-form__button').click()

        # browser.find_element_by_css_selector(
        #     'button.selected-account__clickable').click()

        WebDriverWait(browser, 1000).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.selected-account__clickable'))).click()

        new_address = pyperclip.paste()
        ADDRESSES.append(new_address)
    # END LOOP


def auto_airdrop(browser: WebDriver, eth_address: str):
    browser.get(NFTSEA_URL)
    wait = WebDriverWait(browser, 1000)

    text_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#airdrop-form > div > input'))
    )
    text_field.send_keys(eth_address)

    text_field.send_keys(Keys.RETURN)

    ref_link = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#airdrop-block > div > div.text-break > span.text-primary.copy'))).text
    print(ref_link)

    browser.delete_all_cookies()
    browser.get(ref_link)

    for a in ADDRESSES:
        if a == eth_address:
            continue
        browser.refresh()
        ref_link = keep_refreshing(browser, a)

        print(ref_link)
        browser.delete_all_cookies()


def keep_refreshing(browser: WebDriver, a: str) -> str:
    text_field = WebDriverWait(browser, 1000).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#airdrop-form > div > input'))
    )
    text_field.send_keys(a)
    text_field.send_keys(Keys.RETURN)
    ref_link = ''
    try:
        ref_link = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#airdrop-block > div > div.text-break > span.text-primary.copy'))).text
    except:
        browser.refresh()
        ref_link = keep_refreshing(browser, a)
    return ref_link


if __name__ == '__main__':

    q_table = [
        {
            'type': 'input',
            'qmark': '[?]',
            'name': 'eth_address',
            'message': 'Enter your ethereum address',
        },
        {
            'type': 'input',
            'qmark': '[?]',
            'name': 'seed_phrase',
            'message': 'Input recovery phrase',
        }
    ]
    answer = prompt(q_table, style=custom_style_3)
    RECOVERY_PHRASE = answer['seed_phrase']
    eth_address = answer['eth_address']

    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.add_extension(METAMASK_EXTENSION)
    browser = webdriver.Chrome(CHROME_DRIVER, options=options)
    create_wallets(browser, eth_address)
    auto_airdrop(browser, eth_address)
    # try:
    #     auto_metamask(browser, num)
    # except:
    #     print('[ERROR] A fatal error occoured')

    input('\n\nPress [ENTER] to close browser')
    browser.quit()
