# Selenium Browser Automation Tool 🚀

A Python-based browser automation project built with Selenium WebDriver.

This project automates browser search tasks, supports multiple browsers, captures screenshots, and stores search history automatically.

## Features

✅ Chrome browser support
✅ Firefox browser support
✅ Automated browser control
✅ User-based search input
✅ Automatic screenshot capture
✅ Dynamic screenshot file naming
✅ Search history tracking
✅ Saves search URL
✅ Error handling
✅ Automatic folder creation

---

## Tech Stack

* Python
* Selenium WebDriver
* Chrome WebDriver
* Firefox WebDriver

---

## Project Structure

```text
selenium-google-search/

│
├── screenshots/
│   └── search_output.png
│
├── config.py
├── search.py
├── history.txt
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
```

Go into the project folder:

```bash
cd selenium-google-search
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run Project

```bash
python search.py
```

---

## How It Works

1. User enters a search query
2. User selects browser (Chrome/Firefox)
3. Selenium opens the browser
4. Search is performed automatically
5. Screenshot is captured
6. Search history is saved
7. Browser closes automatically

---

## Example Output

```text
Enter search text: python selenium

Choose browser (chrome/firefox): chrome

Opening browser...
Searching...
Screenshot saved!
Search history updated!
Completed successfully!
```

## Future Improvements

* GUI interface
* Headless automation mode
* Multiple search engine support
* Automated testing framework
* AI-based search assistant

---

## Author

Ashish Sahoo