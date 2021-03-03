from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
#options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))

driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\documents\\chromedriver.exe")
#driver.get("https://forms.arcadia.edu/AUCStatus/?pcid=108319")
driver.get("https://selfservice.arcadia.edu/SelfService/Search/SectionSearch.aspx?sort=CourseId&year=2021&term=SPRING&num=10000")
time.sleep(10)
soup = BeautifulSoup(driver.page_source,"html.parser", encoding = "utf-8")
print(driver.page_source)
driver.quit()