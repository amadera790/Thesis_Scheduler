from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))

driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\AppData\\Local\\Temp\\Rar$EXa20276.12095\\chromedriver.exe")
driver.get("https://forms.arcadia.edu/AUCStatus/?pcid=108319")
time.sleep(10)
soup = BeautifulSoup(driver.page_source,"html.parser")
print(driver.page_source)
driver.quit()