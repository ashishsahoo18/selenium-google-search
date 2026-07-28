"""Desktop Selenium Search Assistant."""

import os
import re
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).parent
SCREENSHOT_FOLDER = BASE_DIR / "screenshots"
HISTORY_FILE = BASE_DIR / "history.txt"

WAIT_TIME = 15

SEARCH_URL = "https://www.google.com"


def improve_query(query):
    """Improve query using OpenAI if an API key is available."""
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

        rewritten = response.output_text.strip()

        return rewritten if rewritten else query

    except Exception:
        # If the AI rewrite fails for any reason, fall back to the
        # original query rather than crashing the search.
        return query


def create_driver(browser, headless):
    """Create and return a Selenium WebDriver for the chosen browser."""
    if browser == "Chrome":
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(options=options)

    if browser == "Firefox":
        options = webdriver.FirefoxOptions()

        if headless:
            options.add_argument("-headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

        return webdriver.Firefox(options=options)

    raise ValueError(f"Unsupported browser: {browser}")


def safe_filename(text):
    """Sanitize text so it can be safely used as a filename."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text).strip(" ._")
    return cleaned or "search"


def get_search_box(wait):
    """Return the clickable Google search input element."""
    return wait.until(EC.element_to_be_clickable((By.NAME, "q")))


def wait_for_results(wait):
    """Block until the Google results container has actually rendered.

    document.readyState hitting "complete" only means the DOM finished
    parsing -- it fires before Google injects its async result blocks,
    images, and ads. Waiting on the real results container (#search)
    is a much more reliable signal that there's something on screen
    worth screenshotting.
    """
    try:
        wait.until(EC.presence_of_element_located((By.ID, "search")))
        return
    except TimeoutException:
        # Fall through to the generic readyState check below -- some
        # result pages (e.g. "no results", a consent wall) never
        # render the #search container.
        pass

    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def run_search(query, browser, headless, use_ai):
    """Run the search on Google, save a screenshot, and log history.

    Returns a tuple of (screenshot_path, searched_query).
    """
    SCREENSHOT_FOLDER.mkdir(exist_ok=True)

    searched_query = improve_query(query) if use_ai else query

    driver = create_driver(browser, headless)

    try:
        if not headless:
            driver.maximize_window()

        driver.get(SEARCH_URL)

        wait = WebDriverWait(driver, WAIT_TIME)

        search_box = get_search_box(wait)
        search_box.clear()
        search_box.send_keys(searched_query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results page to actually load instead of a
        # fixed sleep: the URL should change away from the homepage
        # once the search is submitted.
        wait.until(EC.url_changes(SEARCH_URL))

        # Wait for the actual results container, not just a parsed DOM.
        wait_for_results(wait)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = SCREENSHOT_FOLDER / (
            f"{safe_filename(searched_query)}_{timestamp}.png"
        )

        driver.save_screenshot(str(screenshot_path))

        with HISTORY_FILE.open("a", encoding="utf-8") as file:
            file.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"{browser} | "
                f"{searched_query} | "
                f"{driver.current_url}\n"
            )

        return screenshot_path, searched_query

    finally:
        # Always release the browser process, even if something above
        # raised (timeout, stale element, etc.).
        try:
            driver.quit()
        except WebDriverException:
            pass


class SearchApp(tk.Tk):
    """Main Tkinter application window."""

    def __init__(self):
        super().__init__()

        self.title("Desktop Selenium Search Assistant")
        self.geometry("500x280")
        self.resizable(False, False)

        self.query = tk.StringVar()
        self.browser = tk.StringVar(value="Chrome")
        self.headless = tk.BooleanVar()
        self.use_ai = tk.BooleanVar()
        self.status = tk.StringVar(value="Ready.")

        self.button = None

        self.build_interface()

    def build_interface(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Search Text:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        entry = ttk.Entry(frame, textvariable=self.query, width=42)
        entry.grid(row=0, column=1, columnspan=2, pady=5)
        entry.focus()
        entry.bind("<Return>", lambda event: self.start_search())

        ttk.Label(frame, text="Browser:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        ttk.Combobox(
            frame,
            textvariable=self.browser,
            values=["Chrome", "Firefox"],
            state="readonly",
            width=20,
        ).grid(row=1, column=1, sticky="w")

        ttk.Checkbutton(
            frame, text="Headless Mode", variable=self.headless
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Checkbutton(
            frame, text="Improve Query with AI", variable=self.use_ai
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        self.button = ttk.Button(
            frame,
            text="Search && Take Screenshot",
            command=self.start_search,
        )
        self.button.grid(row=4, column=0, columnspan=3, pady=15)

        ttk.Label(
            frame, textvariable=self.status, wraplength=430
        ).grid(row=5, column=0, columnspan=3, sticky="w")

    def start_search(self):
        query = self.query.get().strip()

        if not query:
            messagebox.showwarning(
                "Missing Search", "Please enter a search query."
            )
            return

        self.button.config(state="disabled")
        self.status.set("Searching... Please wait.")

        threading.Thread(target=self.search_worker, daemon=True).start()

    def search_worker(self):
        query = self.query.get().strip()
        browser = self.browser.get()
        headless = self.headless.get()
        use_ai = self.use_ai.get()

        try:
            screenshot, searched_query = run_search(
                query, browser, headless, use_ai
            )
            self.after(
                0, lambda: self.search_done(screenshot, searched_query, query)
            )

        except TimeoutException:
            self.after(
                0,
                lambda: self.search_failed(
                    "Timed out waiting for the search page to respond. "
                    "Check your internet connection and try again."
                ),
            )

        except WebDriverException as error:
            self.after(
                0,
                lambda: self.search_failed(
                    "Browser automation failed. Make sure the matching "
                    f"WebDriver is installed and on PATH.\n\nDetails: {error}"
                ),
            )

        except Exception as error:  # noqa: BLE001 - surfaced to the user
            self.after(0, lambda: self.search_failed(str(error)))

    def search_done(self, screenshot, searched_query, original_query):
        self.button.config(state="normal")
        self.status.set(
            f"Completed successfully.\nScreenshot: {screenshot.name}"
        )

        try:
            os.startfile(str(screenshot))  # Windows only
        except (AttributeError, OSError):
            # os.startfile doesn't exist on non-Windows platforms, and
            # may also fail if there's no default viewer configured.
            pass

        if self.use_ai.get() and searched_query != original_query:
            messagebox.showinfo(
                "AI Improved Query",
                f"Original:\n\n{original_query}\n\n"
                f"Searched:\n\n{searched_query}",
            )

    def search_failed(self, error):
        self.button.config(state="normal")
        self.status.set("Search failed.")
        messagebox.showerror("Error", error)


if __name__ == "__main__":
    try:
        app = SearchApp()
        app.mainloop()

    except KeyboardInterrupt:
        print("Application closed.")

    except Exception as error:  # noqa: BLE001 - last-resort dialog
        messagebox.showerror("Application Error", str(error))