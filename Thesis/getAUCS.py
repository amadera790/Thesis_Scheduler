from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re
import requests
import json
import random
import unicodedata
import csv
import os
from tqdm import tqdm
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import spacy
import string
import gensim
import operator
from wordcloud import WordCloud
import matplotlib.pyplot as plt
#building word dictionary
from gensim import corpora
from gensim.similarities import MatrixSimilarity
from operator import itemgetter
from IPython import get_ipython

tqdm.pandas()

punctuations = string.punctuation
#creating token object
spacy_nlp = spacy.load('en_core_web_sm')
stop_words = spacy.lang.en.stop_words.STOP_WORDS
descrip_tfidf_corpus = None
descrip_lsi_corpus = None
descrip_tfidf_model = None
descrip_lsi_model = None
dictionary = None
descrip_index = None
df_courses = None
courses = {}
with open('boot.html', 'r') as f:
        html_template = f.read()

# options = webdriver.ChromeOptions()
# options.add_argument('user-data-dir={}'.format('C:\\Users\\BigMo\\AppData\\Local\\Google\\Chrome\\User Data\\Default'))

# driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\BigMo\\AppData\\Local\\Temp\\Rar$EXa20276.12095\\chromedriver.exe")
# driver.get("https://selfservice.arcadia.edu/SelfService/Records/AcademicPlan.aspx")
# time.sleep(10)
# soup = BeautifulSoup(driver.page_source,"html.parser")

def getAUC(auc_File):
    #soup = BeautifulSoup(requests.get(auc_File).content, "html.parser")
    soup = BeautifulSoup(open(auc_File), "html.parser")
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

def getCompletedCourses(html_File):
    soup = BeautifulSoup(open(html_File), "html.parser")
    remaining = [values.text for values in soup.find_all("div",{"class": "classCols"})]
    header = [values.text.strip() for values in soup.find_all("h2",{"class": "tabSliderHeaderLight"})]
    diction = {}
    courseList = {}
    completedList = []
    andList = []
    orList = []
    andPar = []
    Or = False
    And= False 
    andComplete = False
    inProgress = 0
    x = 0

    aucForm = "BioAUCS.html"

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
                if ((td.text.strip() == "(" and header[x] != "300 Level Major Elec" and header[x] != "Major Electives") and td.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text.strip() == "And") or And:
                    And = True
                    try:
                        if all(elem in courseList[header[x]] for elem in andPar):
                            andComplete = True
                    except:
                        pass
                    if td.text.strip() == ")" and td.find_next("td").text.strip() != "Or":
                        And = False
                        if andComplete:
                            for j in andList:
                                if j in courseList[header[x]]:
                                    courseList[header[x]].remove(j)
                        andComplete = False
                        andList.clear()
                    andPar.clear()
                if ((td.text.strip() == "(" and header[x] != "300 Level Major Elec" and header[x] != "Major Electives") and td.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text.strip() == "Or") or Or:
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
                if And and i == 3:
                    andList.append(td.text.strip())
                    andPar.append(td.text.strip())

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

    return courseList, completedList, aucForm

def getSemCourses(year, term):
    page = requests.get("https://selfservice.arcadia.edu/SelfService/Search/SectionSearch.aspx?sort=CourseId&num=10000&year="+year+"&term="+term+"&type=Trad")
    soup = BeautifulSoup(page.content, "html.parser")
    global courses
    coursesSla = {}

    for i in soup.find_all("tr",{"valign": "top"}):
        if i.find("a") is not None and i.find("a").text != "\n\n\t\t\t\tLogin" and "summary=\"Course/Session\"" not in str(i):
           
            
            code = i.find("a").text.split("/")[0]
            slash = i.find("a").text
            courses[code] = {}
            coursesSla[slash] = {}
            link = i.find_next("td").find_next("td").find_next("a")['href']
            try:
                courses[code]["Name"] = i.find_next("td").find_next("td").find_next("span").text.strip()
                coursesSla[slash]["Name"] = i.find_next("td").find_next("td").find_next("span").text.strip()
            except:
                courses[code]["Name"] = "NA"
                coursesSla[slash]["Name"] = "NA"
            try:
                courses[code]["Seats"] = unicodedata.normalize("NFKD", i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(separator = ", "))
                coursesSla[slash]["Seats"] = unicodedata.normalize("NFKD", i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(separator = ", "))            
            except:
                del courses[code]
                del coursesSla[slash]
                continue
            courses[code]["Credits"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
            coursesSla[slash]["Credits"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text

            dayTimeRoom = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text.strip().splitlines()
            try:
                courses[code]["Day"] = dayTimeRoom[0].strip()
                coursesSla[slash]["Day"] = dayTimeRoom[0].strip()
            except:
                courses[code]["Day"] = "NA"
                coursesSla[slash]["Day"] = "NA"
            try:
                courses[code]["Time"] = dayTimeRoom[1].strip()
                coursesSla[slash]["Time"] = dayTimeRoom[1].strip()
            except:
                courses[code]["Time"] = "NA"
                coursesSla[slash]["Time"] = "NA"
            try:
                courses[code]["Room"] = dayTimeRoom[2].strip()
                coursesSla[slash]["Room"] = dayTimeRoom[2].strip()
            except:
                courses[code]["Room"] = "NA"
                coursesSla[slash]["Room"] = "NA"
            try:
                courses[code]["AUCS"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
                coursesSla[slash]["AUCS"] = i.find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").text
            except:
                courses[code]["AUCS"] = ""
                coursesSla[slash]["AUCS"] = ""

            courses[code]["Link"] = link
            coursesSla[slash]["Link"] = link

    return coursesSla


def preReqTerm(year, term):

    page = requests.get("https://selfservice.arcadia.edu/SelfService/Search/SectionSearch.aspx?sort=CourseId&num=10000&year="+year+"&term="+term+"&type=Trad")
    soup = BeautifulSoup(page.content, "html.parser")
    preReqs = {}

    # bar = tqdm(total=len(soup.find_all("tr", {"valign": "top"})))

    first_one = True
    for i in tqdm(soup.find_all("tr", {"valign": "top"})):
        if first_one:
            first_one = False
            continue
        for a in i.find_all("a", href=True):
            if "sectiondetailsdialog" in a['href']:
                page = requests.get(a['href'])
                courseWindow = BeautifulSoup(page.content, "html.parser")
                td = courseWindow.find("td")
                if re.search("(?<=Prerequisites: ).*|(?<=Prerequisite: ).*", td.text) != None:
                    preReqs[td.find_next("span").find_next("span").text.split("/")[0].strip()] = re.search("(?<=Prerequisites: ).*|(?<=Prerequisite: ).*", td.text).group()
                else:
                    preReqs[td.find_next("span").find_next("span").text.split("/")[0].strip()] = "None"

    with open('data.json', 'w') as fp:
        json.dump(preReqs, fp,  indent=4)

def availableCourses(sectionClass, neededAUCS, aucCodes, coursesSla):
    global courses
    global html_template
    preData = open('data.json',)
    preReq = json.load(preData)
    dupe = []
    cdni = []
    csvList = []
    neededMajCourses = []
    neededAucCourses = []
    aucPlaceholder = ""
    print("Availibale Major Courses and Electives")
    for section,neededCor in sectionClass.items():
        for cla in neededCor:
            if cla in courses and courses[cla]:
                neededMajCourses.append(cla)

    writeHtmlFile("majPlaceholder", neededMajCourses)

    print("Availiable Auc requirements")
    for section in coursesSla.keys():
        for key in aucCodes.keys():
            if key in coursesSla[section]["AUCS"]:
                neededAucCourses.append(section)

    writeHtmlFile("aucPlaceholder", neededAucCourses)

def semantic_search():
    global dictionary, spacy_nlp, stop_words, punctuations, descrip_tfidf_model, descrip_lsi_model, descrip_tfidf_corpus, descrip_lsi_corpus, descrip_index, df_courses
    #read in dataset
    df_courses = pd.read_csv('auc.csv', sep='|')
    # adding column name to the respective columns
    df_courses.columns =['Course Code', 'Course Name', 'Instructor', 'Description']
    #data cleaning and processing
    #create list of punctuations and stopwords
    #function for data cleaning and processing
    #This can be further enhanced by adding / removing reg-exps as desired.
    print ('Cleaning and Tokenizing...')
    df_courses = df_courses.drop_duplicates(subset=['Course Code']).reset_index(drop=True)
    df_courses['DescriptionTokenized'] = df_courses['Description'].progress_apply(lambda x: spacy_tokenizer(x))
    courseDescrip = df_courses['DescriptionTokenized']
    courseDescrip[0:5]
    # series = pd.Series(np.concatenate(courseDescrip)).value_counts()[:100]
    # wordcloud = WordCloud(background_color='white').generate_from_frequencies(series)
    # plt.figure(figsize=(15,15), facecolor = None)
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis('off')

    #creating term dictionary
    dictionary = corpora.Dictionary(courseDescrip)
    #list of things which can be further removed
    stoplist = set('hello and if this can would should could tell ask stop come go')
    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
    dictionary.filter_tokens(stop_ids)

    #print top 50 items from the dictionary with their unique token-id
    dict_tokens = [[[dictionary[key], dictionary.token2id[dictionary[key]]] for key, value in dictionary.items() if key <= 50]]

    #bag of words model(BoW)
    #a way of extracting features from text for use in modelling
    #needs a vocab of known word and a measure of the presence of known words

    corpus = [dictionary.doc2bow(desc) for desc in courseDescrip]

    word_frequencies = [[(dictionary[id], frequency) for id, frequency in line] for line in corpus[0:]]

    #build Tf-Idf and LSI Model
    descrip_tfidf_model = gensim.models.TfidfModel(corpus, id2word=dictionary)
    descrip_lsi_model = gensim.models.LsiModel(descrip_tfidf_model[corpus], id2word=dictionary, num_topics=300)

    #serialize and store for easy retrieval
    gensim.corpora.MmCorpus.serialize('descrip_tfidf_model_mm', descrip_tfidf_model[corpus])
    gensim.corpora.MmCorpus.serialize('descrip_lsi_model_mm',descrip_lsi_model[descrip_tfidf_model[corpus]])
    

    descrip_tfidf_corpus = gensim.corpora.MmCorpus('descrip_tfidf_model_mm')
    descrip_lsi_corpus = gensim.corpora.MmCorpus('descrip_lsi_model_mm')

    print(descrip_tfidf_corpus)
    print(descrip_lsi_corpus)

    descrip_index = MatrixSimilarity(descrip_lsi_corpus, num_features = descrip_lsi_corpus.num_terms)

    # search for courses that are related to below search parameters
    keyword = input("Type a word that you would like to recommend classes based on: ")
    print(search_similar_courses(keyword))

def spacy_tokenizer(sentence):
 
    global punctuations
    global stop_words
    #creating token object
    global spacy_nlp
    #remove distracting single quotes
    sentence = re.sub('\'','',sentence)

    #remove digits adnd words containing digits
    sentence = re.sub('\w*\d\w*','',sentence)

    #replace extra spaces with single space
    sentence = re.sub(' +',' ',sentence)
    #remove unwanted lines starting from special charcters
    sentence = re.sub(r'\n: \'\'.*','',sentence)
    sentence = re.sub(r'\n!.*','',sentence)
    sentence = re.sub(r'^:\'\'.*','',sentence)
    
    #remove non-breaking new line characters
    sentence = re.sub(r'\n',' ',sentence)
    
    #remove punctunations
    sentence = re.sub(r'[^\w\s]',' ',sentence)
    
    tokens = spacy_nlp(sentence)

    #lower, strip and lemmatize
    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens]
    #remove stopwords, and exclude words less than 2 characters
    tokens = [word for word in tokens if word not in stop_words and word not in punctuations and len(word) > 2]
    #print(tokens)
    #return tokens
    return tokens

def search_similar_courses(search_term):
    global dictionary, punctuations, spacy_nlp, stop_words, descrip_tfidf_corpus, descrip_lsi_corpus, descrip_lsi_model, descrip_tfidf_model, descrip_index, df_courses
    global courses, html_template
    query_bow = dictionary.doc2bow(spacy_tokenizer(search_term))
    query_tfidf = descrip_tfidf_model[query_bow]
    query_lsi = descrip_lsi_model[query_tfidf]

    descrip_index.num_best = 10

    descrip_list = descrip_index[query_lsi]

    descrip_list.sort(key=itemgetter(1), reverse=True)
    course_names = []
    codes = []
    preData = open('data.json')
    preReq = json.load(preData)
    for j, course in enumerate(descrip_list):
        course_names.append (
            {
                'Relevance': round((course[1] * 100),2),
                'Course Code': df_courses['Course Code'][course[0]],
                'Course Name': df_courses['Course Name'][course[0]],
                'Description': df_courses['Description'][course[0]]
            }
        )
        codes.append(str(df_courses['Course Code'][course[0]]))
        if j == (descrip_index.num_best-1):
            break

    writeHtmlFile("recPlaceholder", codes)

    return codes

def writeHtmlFile(htmlPlaceholder, codes):
    global html_template, courses
    preData = open('data.json')
    preReq = json.load(preData)
    tableCreation = ""
    for cla in codes:
        if "/" in cla:
            cla = cla.split("/")[0]
        tableCreation += '<tr> <td>' + '<a href="'+courses[cla]["Link"]+'" target="_blank">'+ cla + '</a> </td> <td>' + courses[cla]["Name"] + '</td> <td>' + courses[cla]["Seats"] + '</td> <td>' + courses[cla]["Time"] + '</td> <td>' + courses[cla]["Day"] + '</td> <td>' + courses[cla]["Credits"] + '</td>'
        if cla in preReq and courses[cla]:
            tableCreation += "<td>" + preReq[cla] + "</td> </tr>"
        else:
            tableCreation += "<td> </td> </tr>" 

    html_template = html_template.replace(htmlPlaceholder, tableCreation)

    with open('data.html', 'w') as f:
        f.write(html_template)

def makeCSV(year, term):
    page = requests.get("https://selfservice.arcadia.edu/SelfService/Search/SectionSearch.aspx?sort=CourseId&num=10000&year="+year+"&term="+term+"&type=Trad")
    soup = BeautifulSoup(page.content, "html.parser")
    instructors = []
    code = []
    name = []
    des = []
    csvList = []

    for i in soup.find_all("tr", {"valign": "top"}):
        for a in i.find_all("a", href=True):
            if "sectiondetailsdialog" in a['href']:
                cdni = []
                page = requests.get(a['href'])
                courseWindow = BeautifulSoup(page.content, "html.parser")
                td = courseWindow.find("td")
                tr = courseWindow.find("tr")
                br = courseWindow.find("br")
                try:
                    cdni.append(unicodedata.normalize("NFKD", td.find_next("span").find_next("span").text.split("/")[0].strip()))
                except:
                    cdni.append("None")
                try:
                    cdni.append(unicodedata.normalize("NFKD", td.find_next("span").find_next("span").text.split("-")[1].strip()))
                except:
                    cdni.append("None")
                try:
                    ints = unicodedata.normalize("NFKD", tr.find_next("tr").find_next("tr").find_next("tr").find_next("td").find_next("td").text.strip())
                    cdni.append(ints)
                except:
                    cdni.append("None")
                try:
                    p = td.text.strip().splitlines()
                    for x in range(len(p)):
                        if x < len(p) - 3:
                            if re.search("\.00", p[x]):
                                if re.search("Prerequisites:", p[x+3]) or re.search("Prerequisite:", p[x+3]) or re.search("(AUC)", p[x+3]):
                                    k = p[x+2].strip()
                                elif re.search("(AUC)", p[x+2]) or re.search("(AUC)", p[x+3]):
                                        k = "No description provided"
                                else:
                                    k = p[x+2].strip() +""+ p[x+3].strip()
                    if k == '':
                        k = "No description provided"
                    cdni.append(unicodedata.normalize("NFKD",k))
                except:
                    cdni.append("No description provided")

                csvList.append(cdni)
    
    with open('auc.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerows(csvList[:len(csvList)//2])



if __name__ == '__main__':
    
    html_page = input("Enter path to your saved academic html page: ")
    term = input("Enter the term Fall or Spring (summer works but is untested): ")
    year = input("Enter the year: ")
    if not os.path.exists(html_page):
        print('File ' + html_page +' does not exist')
        exit(1)

    makeCSV(year, term)
    preReqTerm(year, term)
    coursesSla = getSemCourses(year, term)
    remCourses, compCourses, aucForm  = getCompletedCourses(html_page)
    neededAUCS, aucCodes = getAUC(aucForm)
    semantic_search()
    availableCourses(remCourses, neededAUCS, aucCodes, coursesSla)


# print(driver.page_source)
#driver.quit()
