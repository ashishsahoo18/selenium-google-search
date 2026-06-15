from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import os
import time

search_text = input("Enter search text: ")

# Create screenshot folder automatically
os.makedirs("screenshots", exist_ok=True)

# Firefox browser
driver = webdriver.Firefox()

try:
    driver.get("https://www.bing.com")

    search_box = driver.find_element(By.NAME, "q")

    search_box.send_keys(search_text)
    search_box.send_keys(Keys.RETURN)

    print("Searching...")

    time.sleep(10)

    # Dynamic screenshot name
    time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"screenshots/{search_text}_{time_now}.png"

    driver.save_screenshot(file_name)

    # Save search history
    with open("history.txt", "a") as file:
        file.write(f"{datetime.now()} - {search_text}\n")

    print("Screenshot saved!")
    print("Search history updated!")

except Exception as e:
    print("Error:", e)

finally:
    print("Closing browser...")
    time.sleep(3)
    driver.quit()