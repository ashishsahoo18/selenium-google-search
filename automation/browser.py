"""Selenium browser factory and search runner."""
from __future__ import annotations

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from search.engines import search_url


class BrowserRunner:
    """Creates a managed Selenium driver and performs a search."""

    def __init__(self, browser: str, headless: bool, incognito: bool) -> None:
        self.browser, self.headless, self.incognito = browser, headless, incognito
        self.driver: webdriver.Remote | None = None

    def _options(self):
        if self.browser in ("Chrome", "Brave"):
            options = ChromeOptions()
            if self.browser == "Brave":
                options.binary_location = "brave.exe"
            if self.incognito: options.add_argument("--incognito")
            if self.headless: options.add_argument("--headless=new")
            return options
        if self.browser == "Edge":
            options = EdgeOptions()
            if self.incognito: options.add_argument("--inprivate")
            if self.headless: options.add_argument("--headless=new")
            return options
        options = FirefoxOptions()
        if self.headless: options.add_argument("-headless")
        if self.incognito: options.add_argument("-private")
        return options

    def open(self) -> None:
        options = self._options()
        if self.browser in ("Chrome", "Brave"):
            self.driver = webdriver.Chrome(options=options)
        elif self.browser == "Edge":
            self.driver = webdriver.Edge(options=options)
        else:
            self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(40)

    def search(self, engine: str, query: str, screenshot: Path) -> str:
        self.open()
        assert self.driver
        self.driver.get(search_url(engine, query))
        self.driver.save_screenshot(str(screenshot))
        return self.driver.current_url

    def close(self) -> None:
        if self.driver:
            self.driver.quit()
