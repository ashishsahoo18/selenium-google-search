from selenium import webdriver
from config import WEBSITE, WAIT_TIME, SCREENSHOT_FOLDER
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import os
import re
import sys
import time

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

search_text = input("Enter search text: ")
browser = input("Choose browser (chrome/firefox): ").lower()

if browser == "chrome":
    driver = webdriver.Chrome()
elif browser == "firefox":
    driver = webdriver.Firefox()
else:
    print("Invalid browser selected")
    sys.exit()

try:
    driver.maximize_window()
    driver.get(WEBSITE)

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_text)
    search_box.send_keys(Keys.RETURN)

    time.sleep(WAIT_TIME)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", search_text)
    screenshot_path = os.path.join(
        SCREENSHOT_FOLDER,
        f"{safe_name}_{timestamp}.png"
    )

    driver.save_screenshot(screenshot_path)

    os.startfile(screenshot_path)  # Opens image in Windows default viewer

    print("Screenshot saved!")

    with open("history.txt", "a", encoding="utf-8") as file:
        file.write(f"{datetime.now()} | {search_text} | {driver.current_url}\n")

    print("Completed successfully!")

except Exception as e:
    print("Error:", e)

finally:
    print("Closing browser...")
    time.sleep(3)
    driver.quit()