import selenium
from selenium import webdriver
from time import sleep
driver = webdriver.Chrome()

driver.get("https://elite.finviz.com/")
sleep(1)