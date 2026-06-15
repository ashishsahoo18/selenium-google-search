from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import os
import time


# Configuration
WEBSITE = "https://www.bing.com"
WAIT_TIME = 10


# Create folders automatically
os.makedirs("screenshots", exist_ok=True)


# User input
search_text = input("Enter search text: ")

browser = input("Choose browser (chrome/firefox): ").lower()


# Browser selection
if browser == "chrome":
    driver = webdriver.Chrome()

elif browser == "firefox":
    driver = webdriver.Firefox()

else:
    print("Invalid browser selected")
    exit()


try:
    print("Opening browser...")

    driver.maximize_window()

    driver.get(WEBSITE)

    print("Searching...")


    # Find search box
    search_box = driver.find_element(By.NAME, "q")

    search_box.send_keys(search_text)
    search_box.send_keys(Keys.RETURN)


    # Wait for results
    time.sleep(WAIT_TIME)


    # Screenshot with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_name = search_text.replace(" ", "_")

    screenshot_path = (
        f"screenshots/{safe_name}_{timestamp}.png"
    )


    driver.save_screenshot(screenshot_path)


    print("Screenshot saved!")


    # Save search history with URL
    with open("history.txt", "a") as file:

        file.write(
            f"{datetime.now()} | "
            f"{search_text} | "
            f"{driver.current_url}\n"
        )


    print("Search history updated!")

    print("Completed successfully!")


except Exception as e:

    print("Error:", e)


finally:

    print("Closing browser...")

    time.sleep(3)

    driver.quit()