import re
import os
import time
import urllib.parse
import urllib

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np

from . import BaseBot, BaseServices


class Services:
    PC = BaseServices.GOOGLE_PC.value


class GoogleBot(BaseBot):
    ROOT_URL = "https://www.google.co.jp/search?q="

    XPATH_SUGGESTION_KEYWORD_PC = '//li[@class="sbct"]//span/text()/parent::node()'
    XPATH_SUGGESTION_INPUT = '//*[@name="q"]'

    XPATH_RELATED_KEYWORD_PC = "//a[@class='k8XOCe R0xfCb VCOFK s8bAkb']"

    XPATH_ALL_RESULT_KEYWORD_PC = '//*[@id="rso"]//a/h3'
    XPATH_ALL_RESULT_LINK_KEYWORD_PC = '//*[@id="rso"]/div//a/h3/parent::a'

    XPATH_PAGINATION = '//*[@id="botstuff"]//table/tbody/tr/td'


    def __init__(
        self, searched_keyword, parameters, *args, **kwargs
    ):
        super(GoogleBot, self).__init__(
            searched_keyword, parameters, *args, **kwargs
        )

        self.services = Services

    def fetch_suggestion(self):

        URL = f"{self.ROOT_URL}+{self.entry_keyword}&start={0}"
        self._get(URL)
        time.sleep(self.TIME_INTERVAL_BASE)
        df_suggestions = self.get_suggestions()
        df_suggestions["rank"] = int(1)
        df_suggestions.to_csv(
            f"out/{self.service}/{self.searched_keyword}/suggestion.csv", index=False
        )
    

    def get_suggestions(self):
        type_ = "SUGGESTION"
        if not os.path.exists(f"out/{self.service}/{self.searched_keyword}"):
            os.makedirs(f"out/{self.service}/{self.searched_keyword}")

        time.sleep(self.TIME_INTERVAL_BASE)
        search = self.driver.find_element(By.XPATH,self.XPATH_SUGGESTION_INPUT)

        self._click(search)

        time.sleep(self.TIME_INTERVAL_BASE)
        self._send_keys(search, Keys.END)
        self._send_keys(search, Keys.SPACE)
        time.sleep(self.TIME_INTERVAL_BASE)
        self.driver.save_screenshot(
            f"out/{self.service}/{self.searched_keyword}/{type_}.png"
        )
        target_xpath = self.XPATH_SUGGESTION_KEYWORD_PC
        els = self.driver.find_elements(By.XPATH, target_xpath)

        suggestions = [el.text for el in els]
        suggestions = [s for s in suggestions if s != ""]
        df_suggestion = pd.DataFrame(suggestions, columns=["title"])
        df_suggestion["title"] = df_suggestion["title"].str.replace("\n", "")
        list_href = [
            self.ROOT_URL + s.replace(" ", "+") for s in suggestions
        ]
        df_href = pd.DataFrame(list_href, columns=["url"])
        df_suggestion = pd.concat([df_suggestion, df_href], axis=1)

        if df_suggestion.empty:
            df_suggestion["title"] = " "
            df_suggestion["url"] = " "

        df_suggestion["type"] = type_

        return df_suggestion


    def fetch_related(self):

        URL = f"{self.ROOT_URL}+{self.entry_keyword}&start={0}"
        self._get(URL)
        time.sleep(self.TIME_INTERVAL_BASE)
        df_related = self.get_relateds()
        df_related["rank"] = int(10)
        df_related.to_csv(
            f"out/{self.service}/{self.searched_keyword}/related.csv", index=False
        )

    def get_relateds(self):
        type_ = "RELATED"
        if not os.path.exists(f"out/{self.service}/{self.searched_keyword}"):
            os.makedirs(f"out/{self.service}/{self.searched_keyword}")

        time.sleep(self.TIME_INTERVAL_BASE)
        search = self.driver.find_element(By.XPATH,self.XPATH_SUGGESTION_INPUT)

        self._click(search)

        time.sleep(self.TIME_INTERVAL_BASE)
        time.sleep(self.TIME_INTERVAL_BASE)

        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, scroll_height)
 
        self.driver.save_screenshot(
            f"out/{self.service}/{self.searched_keyword}/{type_}.png"
        )
        self.driver.save_screenshot(
            f"out/{self.service}/{self.searched_keyword}/{type_}.png"
        )
        target_xpath = self.XPATH_RELATED_KEYWORD_PC
        els = self.driver.find_elements(By.XPATH, target_xpath)

        relateds = [el.text for el in els]
        relateds = [r for r in relateds if r != ""]
        df_related = pd.DataFrame(relateds, columns=["title"])
        df_related["title"] = df_related["title"].str.replace("\n", "")

        list_href = [
            self.ROOT_URL + r.replace(" ", "+") for r in relateds
        ]
        df_href = pd.DataFrame(list_href, columns=["url"])
        df_related = pd.concat([df_related, df_href], axis=1)

        if df_related.empty:
            df_related["title"] = " "
            df_related["url"] = " "

        df_related["type"] = type_

        return df_related
    

    def fetch_all_result(self):
        URL = f"{self.ROOT_URL}+{self.entry_keyword}&start={0}"
        self._get(URL)
        time.sleep(self.TIME_INTERVAL_BASE)
        df_all_result = self.get_all_results()
        df_all_result["rank"] = int(1)
        df_all_result.to_csv(
            f"out/{self.service}/{self.searched_keyword}/page.csv", index=False
        )
    
    def get_all_results(self):
        type_ = "PAGE"
        if not os.path.exists(f"out/{self.service}/{self.searched_keyword}"):
            os.makedirs(f"out/{self.service}/{self.searched_keyword}")


        time.sleep(self.TIME_INTERVAL_BASE)
        search = self.driver.find_element(By.XPATH,self.XPATH_SUGGESTION_INPUT)

        self._click(search)

        time.sleep(self.TIME_INTERVAL_BASE)

        pagination_count = len(WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, self.XPATH_PAGINATION))))

        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, scroll_height)

        self.driver.save_screenshot(
            f"out/{self.service}/{self.searched_keyword}/{type_}.png"
        )

        target_xpath_title = self.XPATH_ALL_RESULT_KEYWORD_PC
        all_results_title = []

        target_xpath = self.XPATH_ALL_RESULT_LINK_KEYWORD_PC
        all_results = []
        page_number = int(self.parameters['PAGE_NUMBER'])
        if pagination_count<page_number and pagination_count!=0:
            page_number=pagination_count
            print(f"There are {page_number} pages data available")

        if pagination_count!=0:
            for page in range(1, page_number+1):
                self.XPATH_PAGINATION = f'//*[@id="botstuff"]//table/tbody/tr/td[{page}]'
                search = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, self.XPATH_PAGINATION)))
                pagination_elements = self.driver.find_elements(By.XPATH, self.XPATH_PAGINATION)

                if len(pagination_elements)>0:
                    self._click(pagination_elements[0])
                    els_title = self.driver.find_elements(By.XPATH, target_xpath_title)
                    all_results_title += [el.text for el in els_title]

                    els = self.driver.find_elements(By.XPATH, target_xpath)
                    all_results += [el.get_attribute('href') for el in els]
                else:
                    print(f"Pagination element for page {page} not found.")

        else:
            print(f"Pagination element is not found.")
        
        all_results_title = [r for r in all_results_title if r != ""]
        df_all_result_title = pd.DataFrame(all_results_title, columns=["title"])
        df_all_result_title["title"] = df_all_result_title["title"].str.replace("\n", "")

        all_results = [r for r in all_results if r != ""]
        df_all_result = pd.DataFrame(all_results, columns=["url"])
        df_all_result["url"] = df_all_result["url"].str.replace("\n", "")

        df_all_result = pd.DataFrame(df_all_result, columns=["url"])
        df_all_result = pd.concat([df_all_result_title, df_all_result], axis=1)

        if df_all_result.empty:
            df_all_result["title"] = " "
            df_all_result["url"] = " "

        df_all_result["type"] = type_

        return df_all_result


    def get_pages_preprocess(self):
        entry_keyword = self.searched_keyword
        _entry_keyword = self.searched_keyword.replace("/", "-")
        self.entry_keyword = entry_keyword = urllib.parse.quote(entry_keyword)
        self.URL = self.ROOT_URL.format(self.entry_keyword)

    def get_pages(self, service):
        self.service = service
        self.get_pages_preprocess()

        print("サイトを取得しました。")
        if "SUGGESTION" in self.parameters:
            if self.parameters["SUGGESTION"]:
                print("サジェストを取得しています。")
                self.fetch_suggestion()
                print("サジェストを取得しました。")
        print("サイトを取得しました。")
        if "RELATED" in self.parameters:
            if self.parameters["RELATED"]:
                print("サジェストを取得しています。")
                self.fetch_related()
                print("サジェストを取得しました。")
        print("サイトを取得しました。")
        if "PAGE" in self.parameters:
            if self.parameters["PAGE"]:
                print("サジェストを取得しています。")
                self.fetch_all_result()
                print("サジェストを取得しました。")
