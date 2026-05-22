from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    time.sleep(15)

    driver.save_screenshot(f"screenshots/{search_text}.png")

    print("Search completed successfully!")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()