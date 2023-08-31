from urllib import parse
import unittest
import sys
import os

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from bots import GoogleBot  # noqa


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **keyworgs):
        super().__init__(*args, **keyworgs)


class TestGoogleBot(BaseTest):
    def setUp(self) -> None:
        event = {}
        self.LOCAL_MODE = 1
        if self.LOCAL_MODE == 1:
            event["async"] = False
        elif self.LOCAL_MODE == 0:
            event["async"] = True
        self.event = event

        self.searched_keyword = "Sports"
        self.service = "GOOGLE_PC"
        self.parameters = {
            "SUGGESTION": True,
            "RELATED": True,
            "PAGE": True,
            "PAGE_NUMBER": 12,
        }
        self.LOCAL_DEBUG = int(os.environ.get("LOCAL_DEBUG", 0))

        return super().setUp()

    def test_get_page_pc(self):
        google_bot = GoogleBot(
            self.searched_keyword,
            service=self.service,
            parameters=self.parameters,
        )
        google_bot.init_driver_local_chrome_debug() if self.LOCAL_DEBUG else google_bot.init_driver_local_chrome()
        google_bot.get_pages_pc()
        google_bot.close()
        google_bot.quit()
