import logging
import random
import sys
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from seleniumwire.inspect import InspectRequestsMixin

from db import DatabaseConnection
from json_reader import parse_json
from request_handler import decode_json_response


def scroll_to_bottom(driver: WebDriver):
    # We don't know exactly how long it'll take to get to the bottom...
    # ...so let's wait 3-4 minutes?
    end = time.time() + 180
    while time.time() < end:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        # Delay for a bit of random time, to simulate rapid scrolling down a page
        time.sleep(random.randint(1, 3))
        try:
            # Reference: https://stackoverflow.com/a/3923863/1079354
            # tl;dr: find the ancestor of the element that contains the text "retry" to click it
            # If something happens, or there's a timeout, we have to retry the request.
            # Problem is that it's not a link, but a really fancy-looking div that has the role of a button.
            # Just clicking on the text doesn't fire off the JS event; you have to click the div itself as if it
            # were a button.  So, the XPath here accomplishes finding that element for us.
            driver.find_element(value="//text()[contains(.,'Retry')]/ancestor::*[self::div][1]", by=By.XPATH).click()
            print("Had to retry the connection!")
        except NoSuchElementException as e:
            # Explicitly silenced - not being able to find the button is perfectly normal
            pass


def collate_bookmarks(db: DatabaseConnection, driver: InspectRequestsMixin) -> None:
    for request in driver.requests:
        if "Bookmarks?variables=" in request.url and request.response:
            unparsed_tweets = decode_json_response(request.response)
            parsed_tweets = parse_json(unparsed_tweets)
            db.insert_into_database(parsed_tweets)


def bookmarks_element(driver):
    return driver.find_element(value="Bookmarks", by=By.LINK_TEXT)


def main():
    db = DatabaseConnection()
    driver = webdriver.Firefox()
    driver.get("https://www.twitter.com")

    WebDriverWait(driver, timeout=200).until(bookmarks_element)
    time.sleep(10)
    bookmarks_element(driver).click()
    time.sleep(20)
    scroll_to_bottom(driver)
    collate_bookmarks(db, driver)


if __name__ == '__main__':
    main()
