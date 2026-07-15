"""Desktop Selenium search assistant."""

import os
import time
import re
import threading
from datetime import datetime, time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

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
    """Improve the search query only if an OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return query

    try:
        from openai import OpenAI

        response = OpenAI(api_key=api_key).responses.create(
            model="gpt-4.1-mini",
            input=(
                "Rewrite this as one concise and useful web-search query. "
                "Return only the query: " + query
            ),
        )

        improved = response.output_text.strip()
        return improved or query

    except Exception:
        return query


def create_driver(browser, headless):
    if browser == "Chrome":
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(options=options)

    options = webdriver.FirefoxOptions()

    if headless:
        options.add_argument("-headless")

    return webdriver.Firefox(options=options)


def safe_filename(value):
    return re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        value
    ).strip(" ._") or "search"


def run_search(query, engine, browser, headless, use_ai):
    SCREENSHOT_FOLDER.mkdir(exist_ok=True)

    searched_query = improve_query(query) if use_ai else query
    driver = create_driver(browser, headless)

    try:
        if not headless:
            driver.maximize_window()

        driver.get(SEARCH_ENGINES[engine])

        wait = WebDriverWait(driver, WAIT_TIME)

        search_box = wait.until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )

        search_box.send_keys(searched_query)
        search_box.send_keys(Keys.RETURN)

        wait.until(
            lambda d: d.current_url != SEARCH_ENGINES[engine]
        )

        time.sleep(20)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_path = SCREENSHOT_FOLDER / (
            f"{safe_filename(searched_query)}_{timestamp}.png"
        )

        driver.save_screenshot(str(screenshot_path))

        with HISTORY_FILE.open("a", encoding="utf-8") as history:
            history.write(
                f"{datetime.now().isoformat(sep=' ', timespec='seconds')} | "
                f"{engine} | {searched_query} | "
                f"{driver.current_url}\n"
            )

        return screenshot_path, searched_query

    finally:
        driver.quit()


class SearchApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Selenium Search Assistant")
        self.resizable(False, False)

        self.query = tk.StringVar()
        self.engine = tk.StringVar(value="Google")
        self.browser = tk.StringVar(value="Chrome")
        self.headless = tk.BooleanVar()
        self.use_ai = tk.BooleanVar()

        self.status = tk.StringVar(
            value="Enter a search and press Search."
        )

        self.build_interface()

    def build_interface(self):
        frame = ttk.Frame(self, padding=18)
        frame.grid()

        ttk.Label(frame, text="Search text:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        entry = ttk.Entry(
            frame,
            textvariable=self.query,
            width=42
        )
        entry.grid(row=0, column=1, columnspan=2, pady=5)
        entry.focus()

        ttk.Label(frame, text="Search engine:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        ttk.Combobox(
            frame,
            textvariable=self.engine,
            values=list(SEARCH_ENGINES),
            state="readonly",
            width=18
        ).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Browser:").grid(
            row=2, column=0, sticky="w", pady=5
        )

        ttk.Combobox(
            frame,
            textvariable=self.browser,
            values=["Chrome", "Firefox"],
            state="readonly",
            width=18
        ).grid(row=2, column=1, sticky="w")

        ttk.Checkbutton(
            frame,
            text="Headless mode (do not show browser)",
            variable=self.headless
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=4)

        ttk.Checkbutton(
            frame,
            text="Improve query with AI (optional API key)",
            variable=self.use_ai
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=4)

        self.button = ttk.Button(
            frame,
            text="Search and Screenshot",
            command=self.start_search
        )
        self.button.grid(row=5, column=0, columnspan=3, pady=(10, 6))

        ttk.Label(
            frame,
            textvariable=self.status,
            wraplength=400
        ).grid(row=6, column=0, columnspan=3, sticky="w")

    def start_search(self):
        if not self.query.get().strip():
            messagebox.showwarning(
                "Missing search",
                "Please enter search text."
            )
            return

        self.button.config(state="disabled")
        self.status.set("Searching...")

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
                lambda: self.search_done(screenshot, searched_query)
            )

        except Exception as error:
            self.after(
                0,
                lambda: self.search_failed(str(error))
            )

    def search_done(self, screenshot, searched_query):
        self.status.set(f"Done. Screenshot: {screenshot.name}")
        self.button.config(state="normal")

        os.startfile(screenshot)

        if self.use_ai.get() and searched_query != self.query.get().strip():
            messagebox.showinfo(
                "AI search query",
                f"Searched for: {searched_query}"
            )

    def search_failed(self, error):
        self.status.set("Search failed.")
        self.button.config(state="normal")

        messagebox.showerror("Search error", error)


if __name__ == "__main__":
    SearchApp().mainloop()