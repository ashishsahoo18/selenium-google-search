from selenium import webdriver

print("Starting Chrome...")

driver = webdriver.Chrome()

print("Chrome started!")

driver.get("https://www.google.com")

print(driver.title)

driver.quit()