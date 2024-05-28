from selenium import webdriver

driver = webdriver.Chrome()
print(driver.capabilities['browserVersion'])
driver.quit()