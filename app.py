"""Desktop Selenium Search Assistant"""

import os
import re
import time
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).parent
SCREENSHOT_FOLDER = BASE_DIR / "screenshots"
HISTORY_FILE = BASE_DIR / "history.txt"

WAIT_TIME = 15

SEARCH_ENGINES = {
    "Google": "https://www.google.com",
    "Bing": "https://www.bing.com",
    "DuckDuckGo": "https://duckduckgo.com",
}


def improve_query(query):
    """Improve query using OpenAI if API key exists."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return query

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=(
                "Rewrite this as a short and effective web search query. "
                "Return only the rewritten query.\n\n"
                f"{query}"
            ),
        )

        return response.output_text.strip()

    except Exception:
        return query


def create_driver(browser, headless):

    if browser == "Chrome":

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(options=options)

    else:

        options = webdriver.FirefoxOptions()

        if headless:
            options.add_argument("-headless")

        return webdriver.Firefox(options=options)


def safe_filename(text):

    return re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        text
    ).strip(" ._") or "search"


def get_search_box(wait, engine):

    if engine == "Google":
        return wait.until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )

    if engine == "Bing":
        return wait.until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )

    if engine == "DuckDuckGo":
        return wait.until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )

    raise Exception("Unsupported search engine")


def run_search(query, engine, browser, headless, use_ai):

    SCREENSHOT_FOLDER.mkdir(exist_ok=True)

    searched_query = improve_query(query) if use_ai else query

    driver = create_driver(browser, headless)

    try:

        if not headless:
            driver.maximize_window()

        driver.get(SEARCH_ENGINES[engine])

        wait = WebDriverWait(driver, WAIT_TIME)

        search_box = get_search_box(wait, engine)

        search_box.clear()

        search_box.send_keys(searched_query)

        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_path = SCREENSHOT_FOLDER / (
            f"{safe_filename(searched_query)}_{timestamp}.png"
        )

        driver.save_screenshot(str(screenshot_path))

        with HISTORY_FILE.open("a", encoding="utf-8") as file:

            file.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"{engine} | "
                f"{searched_query} | "
                f"{driver.current_url}\n"
            )

        return screenshot_path, searched_query

    finally:
        driver.quit()


class SearchApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Desktop Selenium Search Assistant")

        self.geometry("500x310")

        self.resizable(False, False)

        self.query = tk.StringVar()

        self.engine = tk.StringVar(value="Google")

        self.browser = tk.StringVar(value="Chrome")

        self.headless = tk.BooleanVar()

        self.use_ai = tk.BooleanVar()

        self.status = tk.StringVar(
            value="Ready."
        )

        self.build_interface()

        def build_interface(self):

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Search Text:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=5
        )

        entry = ttk.Entry(
            frame,
            textvariable=self.query,
            width=42
        )

        entry.grid(
            row=0,
            column=1,
            columnspan=2,
            pady=5
        )

        entry.focus()

        entry.bind(
            "<Return>",
            lambda event: self.start_search()
        )

        ttk.Label(
            frame,
            text="Search Engine:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        ttk.Combobox(
            frame,
            textvariable=self.engine,
            values=list(SEARCH_ENGINES.keys()),
            state="readonly",
            width=20
        ).grid(
            row=1,
            column=1,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Browser:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        ttk.Combobox(
            frame,
            textvariable=self.browser,
            values=["Chrome", "Firefox"],
            state="readonly",
            width=20
        ).grid(
            row=2,
            column=1,
            sticky="w"
        )

        ttk.Checkbutton(
            frame,
            text="Headless Mode",
            variable=self.headless
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=5
        )

        ttk.Checkbutton(
            frame,
            text="Improve Query with AI",
            variable=self.use_ai
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=5
        )

        self.button = ttk.Button(
            frame,
            text="Search && Take Screenshot",
            command=self.start_search
        )

        self.button.grid(
            row=5,
            column=0,
            columnspan=3,
            pady=15
        )

        ttk.Label(
            frame,
            textvariable=self.status,
            wraplength=430
        ).grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w"
        )

        def start_search(self):

        query = self.query.get().strip()

        if not query:
            messagebox.showwarning(
                "Missing Search",
                "Please enter a search query."
            )
            return

        self.button.config(state="disabled")

        self.status.set("Searching... Please wait.")

        threading.Thread(
            target=self.search_worker,
            daemon=True
        ).start()


    def search_worker(self):

        try:

            screenshot, searched_query = run_search(
                self.query.get().strip(),
                self.engine.get(),
                self.browser.get(),
                self.headless.get(),
                self.use_ai.get()
            )

            self.after(
                0,
                lambda: self.search_done(
                    screenshot,
                    searched_query
                )
            )

        except Exception as error:

            self.after(
                0,
                lambda: self.search_failed(str(error))
            )


    def search_done(self, screenshot, searched_query):

        self.button.config(state="normal")

        self.status.set(
            f"Completed successfully.\nScreenshot: {screenshot.name}"
        )

        try:
            os.startfile(str(screenshot))
        except Exception:
            pass

        if (
            self.use_ai.get()
            and searched_query != self.query.get().strip()
        ):

            messagebox.showinfo(
                "AI Improved Query",
                f"Original:\n\n{self.query.get()}\n\n"
                f"Searched:\n\n{searched_query}"
            )


    def search_failed(self, error):

        self.button.config(state="normal")

        self.status.set("Search failed.")

        messagebox.showerror(
            "Error",
            error
        )


if __name__ == "__main__":
    SearchApp().mainloop()