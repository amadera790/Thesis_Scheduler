import re
from bs4 import BeautifulSoup
from pandas import Series, DataFrame
import pandas as pd
from selenium import webdriver
import time 


def dump(data, j, length):
    if (j % 200 == 0 and j != 0) or j == length - 1:
        df = DataFrame(data)
        df.to_json(''.join(['data_dump_',str(j),'.json']))
        print(''.join(["Dumping up to ", str(j)]))


def crawl():
    ids = []
    with open('user_ids.txt') as fp:
        ids = fp.readlines()
    
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))
    browser = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\AppData\\Local\\Temp\\Rar$EXa20276.12095\\chromedriver.exe")

    data = {}

    name = 0
    length = len(ids)
    for j, user_id in enumerate(ids):
        try:
            browser.get('https://selfservice.arcadia.edu/SelfService//Advising/ClassSchedule.aspx?studentId=' + str(user_id))
            if j == 0: time.sleep(100)  # allows us to log in for the first time
            soup = BeautifulSoup(browser.page_source,"html.parser")

            if 'Expected Full Time' in str(soup):
                dump(data, j, length)
                continue

            file_a = str(soup("a"))
            Classes = re.findall("(\w+/.+/\d+)\s-\s.+?</a>",file_a)

            file_td = str(soup("td"))
            Times_found = re.findall("(\w+)\s+(\d+:\d+\s\w+\s-\s\d+:\d+\s\w+)\s+;?",file_td)
            Times = Times_found[:len(Classes)]

            file_td = str(soup("td"))
            Rooms_found = re.findall("\w+\s+\d+:\d+\s\w+\s-\s\d+:\d+\s\w+\s+;\s+(.+)\s+</td>?",file_td)

            Rooms = Rooms_found[:len(Classes)]
            for i in range(0, len(Rooms)):
                if Rooms[i] == "Arcadia Univ, , Room ":
                    Rooms[i] = "Unknown"

            data[name] = {"Classes": Classes, "Times": Times, "Rooms": Rooms}
            name += 1
        except:
            print("Some error happened while processing id = ", user_id)
        
        print(''.join(["Working on ", str(j)]))

        dump(data, j, length)


def load_tester():
    df = pd.read_json('data_dump.json')
    print(df[3])


if __name__ == "__main__":
    crawl()
    # load_tester()
