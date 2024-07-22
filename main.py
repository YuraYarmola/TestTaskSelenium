import hashlib
import json
import logging
import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import traceback
import os


class LATimesScraper:
    def __init__(self, config_path):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        with open(config_path, 'r') as file:
            self.config = json.load(file)
        self.base_url = "https://www.latimes.com/"
        self.results = []

    def search_news(self):
        self.driver.get(self.base_url)
        self.driver.find_element(By.XPATH, '//button[@data-element="search-button"]').click()
        time.sleep(1)
        search_box = self.driver.find_element(By.XPATH, "//input[@data-element='search-form-input']")
        search_box.send_keys(self.config["search_phrase"])
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

    def filter_news_by_category(self):
        if self.config["news_category"]:
            try:
                self.driver.find_element(By.XPATH, '//button[@class="button filters-open-button"]').click()
                time.sleep(0.5)
                self.driver.find_element(By.XPATH, '//button[@class="button see-all-button"]').click()
                time.sleep(0.5)
                for category_name in self.config["news_category"]:
                    try:
                        category_filter = self.driver.find_element(By.XPATH,  f"//label[contains(., '{category_name}')]")
                        category_filter.find_element(By.TAG_NAME, "input").click()
                    except Exception as e:
                        logging.error(f"Category filter error for category: {category_name} -  {e}")

                self.driver.find_element(By.XPATH, "//button[@class='button apply-button']").click()
                time.sleep(10)
            except Exception as e:
                print(f"Category filter error: {e}")

    def sort_by(self, sort_by="Newest"):
        select_element = self.driver.find_element(By.XPATH, "//select[@class='select-input']")
        select = Select(select_element)
        select.select_by_visible_text(sort_by)

    def get_news_within_months(self):
        months = self.config["months"]
        date_limit = datetime.now() - timedelta(days=30 * months)
        download_folder = self.config["download_folder"]

        # Create the download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        continue_search = True
        while continue_search:
            article_menu = self.driver.find_element(By.XPATH, "//ul[@class='search-results-module-results-menu']")
            articles = article_menu.find_elements(By.XPATH, "./li")

            for article in articles:
                try:
                    title = article.find_element(By.XPATH, ".//h3[@class='promo-title']").text
                    description = article.find_element(By.XPATH, ".//p[@class='promo-description']").text
                    timestamp = article.find_element(By.XPATH, ".//p[@class='promo-timestamp']").get_attribute(
                        "data-timestamp")
                    media_url = article.find_element(By.XPATH, ".//div[@class='promo-media']").find_element(By.XPATH,
                                                                                                            ".//img[@class='image']").get_attribute(
                        "src")

                    article_date = datetime.fromtimestamp(int(timestamp) / 1000)

                    if article_date < date_limit:
                        continue_search = False
                        break
                    response = requests.get(media_url)
                    media_content = response.content
                    media_hash = hashlib.sha256(media_content).hexdigest()
                    media_filename = os.path.join(download_folder, f"{media_hash}.jpg")
                    with open(media_filename, 'wb') as file:
                        file.write(media_content)

                    self.results.append({
                        "title": title,
                        "date": article_date.strftime('%Y-%m-%d'),
                        "description": description,
                        "image_filename": media_filename,
                        "count_of_search_phrases": title.lower().count(
                            self.config["search_phrase"].lower()) + description.lower().count(
                            self.config["search_phrase"].lower()),
                        "contains_money": bool(
                            re.search(r'\$\d+(\.\d{2})?|(\d+ )?dollars|USD', title + ' ' + description))
                    })

                except Exception as e:
                    logging.error(f"Error processing article: {e}")

            if continue_search:
                next_page = self.driver.find_element(
                    By.XPATH, "//div[@class='search-results-module-next-page']").find_element(By.XPATH,
                                                                                                ".//a").get_attribute(
                    "href")
                self.driver.get(next_page)

    def save_to_excel(self):
        df = pd.DataFrame(self.results)
        df.to_excel('news_results.xlsx', index=False)

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    config_path = "config.json"
    scraper = LATimesScraper(config_path)
    try:
        scraper.search_news()
        scraper.filter_news_by_category()
        scraper.sort_by()
        scraper.get_news_within_months()
        scraper.save_to_excel()
    finally:
        scraper.close()
