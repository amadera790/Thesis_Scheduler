from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re

# options = webdriver.ChromeOptions()
# options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))

# driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\AppData\\Local\\Temp\\Rar$EXa20276.12095\\chromedriver.exe")
# driver.get("https://selfservice.arcadia.edu/SelfService/Records/AcademicPlan.aspx")
# time.sleep(10)
# soup = BeautifulSoup(driver.page_source,"html.parser")
soup = BeautifulSoup(open('AUCS.html'), "html.parser")

courses_tags    = [values.text for values in soup.findAll(id="Courses")]
categories_tags = [values.text for values in soup.findAll(id="Category")]

AUC = {}

for i, category in enumerate(categories_tags):
    category = re.search('\s{2,}(.*)', category)
    if category:
        course_list  = re.findall('[A-Z]{2}[0-9]{3}\.[0-9A-Z]{1,3}', courses_tags[i])
        AUC[category.group(1)] = course_list

#print(AUC)

for key, values in AUC.items():
    if '2 ' in key:
        if len(values) < 2:
            print(key)

    elif len(values) == 0:
        print(key)
            


# print(driver.page_source)
#driver.quit()