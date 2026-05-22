from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Open Chrome
driver = webdriver.Chrome()

# Open Google
driver.get("https://www.google.com")

# Find search box
search = driver.find_element(By.NAME, "q")

# Type text
search.send_keys("Python Selenium Tutorial")

# Wait 2 seconds
time.sleep(2)

# Close browser
driver.quit()