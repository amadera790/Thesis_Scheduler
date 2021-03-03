from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re
import requests
import json
import random
import unicodedata

# options = webdriver.ChromeOptions()
# options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))

# driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\AppData\\Local\\Temp\\Rar$EXa20276.12095\\chromedriver.exe")
# driver.get("https://selfservice.arcadia.edu/SelfService/Records/AcademicPlan.aspx")
# time.sleep(10)
# soup = BeautifulSoup(driver.page_source,"html.parser")

def getAUC() -> (dict, list):
    soup = BeautifulSoup(open('BioAUCS.html'), "html.parser")

    courses_tags    = [values.text for values in soup.findAll(id="Courses")]
    categories_tags = [values.text for values in soup.findAll(id="Category")]
    code_tags = [values.text for values in soup.findAll(id="Code")]
    placement_tags  = [values.text.strip() for values in soup.findAll(id="Score")]

    AUC = {}
    Code = {}
    Needed = {}
  

    for i, _ in enumerate(categories_tags):
        category = re.search('\s{2,}(.*)', categories_tags[i])
        code_tag = re.search('\s{2,}(.*)', code_tags[i])
        if category:
            course_list  = re.findall('[A-Z]{2}[0-9]{3}\.[0-9A-Z]{1,3}', courses_tags[i])

            AUC[category.group(1)] = course_list
            Code[code_tag.group(1)[0:-1]] = course_list


    print(AUC)
    print(Code)

    try:
        if len(AUC.get("Natural/Physical World (or 2nd NPL)")) < 1 and len(AUC.get("Natural/Physical World with Lab")) > 1:
            #delete NP's if you have 2 or more NPLs and 0 NP's
            del AUC["Natural/Physical World (or 2nd NPL)"]
    except:
        pass

    try:
        if len(AUC.get("Quantitative Reasoning (or 2nd QRM)")) < 1 and len(AUC.get("Quantitative Reasoning Mathematics")) > 1:
            #delete QR's if you have 2 or more QRM's but 0 QR's
            del AUC["Quantitative Reasoning (or 2nd QRM)"]
    except:
        pass

    needed_AUC = {}

    for key, values in AUC.items():

        if '2 ' in key:
            if len(values) < 2:
                needed_AUC[key] = values

        elif len(values) == 0:
            needed_AUC[key] = values
                
    Needed = Code.copy()
    remove = []

    for key in Code:
        if key in ['-CL-', '-W-', '-SS-', '-CB-']:
            if len(Needed[key]) >= 2:
                remove.append(key)
        elif key in ['-NPL-', '-NP-']:
            if len(Needed['-NPL-']) >= 2 or (len(Needed['-NPL-']) > 0 and len(Needed['-NP-']) > 0):
                remove.append(key)
        elif key in ['-QRM-', '-QR-']:
            if len(Needed['-QRM-']) >= 2 or (len(Needed['-QRM-']) > 0 and len(Needed['-QR-']) > 0):
                remove.append(key)
        else:
            if len(Needed[key]) > 0:
                remove.append(key)

    for key in remove:
        del Needed[key]
        
    print(Needed)
    print(needed_AUC)
    return needed_AUC, Needed

def getMaj():
    

    soup = BeautifulSoup(open('BioPlan.html'), "html.parser")

    # parse remaining list
    remaining = []
    section = []
    sectionClass = {}
    Or = False
    orList = []
    
    for name in soup.find_all("a", {"href": "javascript:void(0)"}):
        section.append(name.text.strip())

    section = section[1:-1]

    for t, major in enumerate(soup.find_all("table",{"class": "defaultTableAlignTop"})):
        # remaining[t] - this will be the remaining number of courses for this specific table
        sectionClass[section[t]] = []
        for tr in major.find_all("tr"):
            completed, in_progress = False, False
            for i, td in enumerate(tr.find_all("td")):
                if td.text.strip() == "(" and section[t] != "300 Level Major Elec" and section[t] != "Major Electives":
                    Or = True
                if td.text.strip() == ")":
                    Or = False
                    for orIndex in orList:
                        if not (orIndex in sectionClass[section[t]]):
                            for k in orList:
                                if k in sectionClass[section[t]]:
                                    sectionClass[section[t]].remove(k)
                    orList.clear()
                if td.find("a") and td.find("a")["title"] == "Completed":
                    completed = True
                if td.find("a") and td.find("a")["title"] == "In Progress":
                    in_progress = True
                if i == 3 and not completed and not in_progress:
                    sectionClass[section[t]].append(td.text.strip())

    print(sectionClass)
    return sectionClass

    '''
    major_tags = soup.find("table", {"class": "defaultTableAlignTop"})
    major = [values.text for values in major_tags.find_all("a")]
    print(major)
    
    major_Tags = [values.text for values in soup.find("table", {"class": "defaultTableAlignTop"})]
    major = 
    
    for atag in majorTags:
        atags = [values.text for values in soup.find_all("a")]
        print(atags)
    '''
def getCompletedCourses():
    soup = BeautifulSoup(open('BioPlan.html'), "html.parser")
    remaining = [values.text for values in soup.find_all("div",{"class": "classCols"})]
    header = [values.text.strip() for values in soup.find_all("h2",{"class": "tabSliderHeaderLight"})]
    diction = {}
    courseList = {}
    completedList = []
    orList = []
    Or = False
    inProgress = 0
    x = 0

    for line in remaining:
        if (re.search("Courses",line)):
            xyz = re.search("([0-9]+)(?!.*[0-9])",line)
            xyz = int(xyz.group())
            diction[header[x]] = xyz
            x=x+1

    x = 0
    del diction["Courses Not Assigned to this Academic Plan"]

    for t, major in enumerate(soup.find_all("table",{"class": "defaultTableAlignTop"})):
        inProgress = 0
        for tr in major.find_all("tr"):
            completed, in_progress = False, False
            for i, td in enumerate(tr.find_all("td")):
                if td.text.strip() == "(" and header[x] != "300 Level Major Elec" and header[x] != "Major Electives":
                    Or = True
                if td.text.strip() == ")":
                    Or = False
                    for orIndex in orList:
                        if not (orIndex in courseList[header[x]]):
                            for k in orList:
                                if k in courseList[header[x]]:
                                    courseList[header[x]].remove(k)
                    orList.clear()

                if td.find("a") and td.find("a")["title"] == "Completed":
                    completed = True
                if td.find("a") and td.find("a")["title"] == "In Progress":
                    inProgress = inProgress + 1
                    in_progress = True
                if i == 3 and not completed and not in_progress:
                    if header[x] not in courseList:
                        courseList[header[x]] = []
                    courseList[header[x]].append(td.text.strip())
                if i == 3 and (completed or in_progress):
                    completedList.append(td.text.strip())
                if Or and i == 3:
                    orList.append(td.text.strip())

        diction[header[x]] = diction.get(header[x]) - inProgress 
        x=x+1

    for k in soup.find_all("table", {"class": "text75em"}):
        for tr in k.find_all("tr"):
            for td in tr.find_all("td"):
                try:
                    if(td.find("img")["title"] == "Course has been completed." or td.find("img")["title"] == "In Progress"):
                        completedList.append(td.find_next("td").text.strip())
                except:
                    continue

    print(completedList)
    print(courseList)
    return courseList, completedList

def getSemCourses():

    soup = BeautifulSoup(open('springSem2021.html'), "html.parser")
    courses = {}
    coursesSla = {}

    for i in soup.find_all("tr",{"valign": "top"}):
        if i.find("a") is not None and i.find("a").text != "\n\n\t\t\t\tLogin" and "summary=\"Course/Session\"" not in str(i):
           
            
            name = i.find("a").text.split("/")[0]
            slash = i.find("a").text
            courses[name] = {}
            coursesSla[slash] = {}
            try:
                courses[name]["Seats"] = unicodedata.normalize("NFKD", i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(separator = ", "))
                coursesSla[slash]["Seats"] = unicodedata.normalize("NFKD", i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(separator = ", "))            
            except:
                del courses[name]
                del coursesSla[slash]
                continue
            courses[name]["Credits"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
            coursesSla[slash]["Credits"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text

            dayTimeRoom = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text.strip().splitlines()
            try:
                courses[name]["Day"] = dayTimeRoom[0].strip()
                coursesSla[slash]["Day"] = dayTimeRoom[0].strip()
            except:
                courses[name]["Day"] = "NA"
                coursesSla[slash]["Day"] = "NA"
            try:
                courses[name]["Time"] = dayTimeRoom[1].strip()
                coursesSla[slash]["Time"] = dayTimeRoom[1].strip()
            except:
                courses[name]["Time"] = "NA"
                coursesSla[slash]["Time"] = "NA"
            try:
                courses[name]["Room"] = dayTimeRoom[2].strip()
                coursesSla[slash]["Room"] = dayTimeRoom[2].strip()
            except:
                courses[name]["Room"] = "NA"
                coursesSla[slash]["Room"] = "NA"
            try:
                courses[name]["AUCS"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
                coursesSla[slash]["AUCS"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
            except:
                courses[name]["AUCS"] = ""
                coursesSla[slash]["AUCS"] = ""

    return courses, coursesSla


def currentSem():

    #(?<=\Prerequisites: ).*
    soup = BeautifulSoup(open('springSem2021.html'), "html.parser")
    preReqs = {}

    for i in soup.find_all("tr", {"valign": "top"}):
        for a in i.find_all("a", href=True):
            if "sectiondetailsdialog" in a['href']:
                print(a['href'])
                page = requests.get(a['href'])
                courseWindow = BeautifulSoup(page.content, "html.parser")
                td = courseWindow.find("td")
                if re.search("(?<=Prerequisites: ).*|(?<=Prerequisite: ).*", td.text) != None:
                    preReqs[td.find_next("span").find_next("span").text.split("\/")[0]] = re.search("(?<=Prerequisites: ).*|(?<=Prerequisite: ).*", td.text).group()
                else:
                    preReqs[td.find_next("span").find_next("span").text.split("\/")[0]] = "None"

    with open('data.json', 'w') as fp:
        json.dump(preReqs, fp,  indent=4)

def availableCourses(courses, sectionClass, neededAUCS, aucCodes, coursesSla):
    preData = open('data.json',)
    preReq = json.load(preData)
    dupe = []
    print("Availibale Major Courses and Electives")
    for section,neededCor in sectionClass.items():
        for cla in neededCor:
            if cla in courses and courses[cla] not in dupe:
                print(cla + " " + str(courses[cla]))
                if cla in preReq and courses[cla] not in dupe:
                    print(preReq[cla])
                dupe.append(courses[cla])

    print("Availiable Auc requirements")
    for section in coursesSla.keys():
        for key in aucCodes.keys():
            if key in coursesSla[section]["AUCS"]:
                print(section + " " +str(coursesSla[section]))
                break
    


neededAUCS, aucCodes = getAUC()
remCourses, compCourses  = getCompletedCourses()
courses, coursesSla = getSemCourses()
availableCourses(courses, remCourses, neededAUCS, aucCodes, coursesSla)

'''
courseList = {}
courses = {}

courses = getSemCourses()
courseList = getNumofCourses()
available = {}

print(courseList)
print(courses)

for key in courseList:
    for k in range(len(courseList[key])):
        for x in courses:
            if courseList[key][k] in x:
                if key not in available:
                    available[key] = []
                available[key].append(x)

print(available)



if __name__ == '__main__':
    AUC, placement_tags = getAUC()
    print(AUC, placement_tags)
([0-9]+)(?!.*[0-9])
(\d+)(?!.*\d)
# print(driver.page_source)
#driver.quit()
'''