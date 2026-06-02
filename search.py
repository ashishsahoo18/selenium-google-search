from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time

search_text = input("Enter search text: ")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.bing.com")

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_text)
    search_box.send_keys(Keys.RETURN)

    print("Searching...")

    time.sleep(20)

    # Save screenshot
    driver.save_screenshot(f"screenshots/{search_text}.png")

    # Save search history
    with open("history.txt", "a") as file:
        file.write(f"{datetime.now()} - {search_text}\n")

    print("Screenshot saved!")
    print("Search history updated!")

except Exception as e:
    print("Error:", e)

finally:
    print("Browser closing...")
    time.sleep(3)
    driver.quit()