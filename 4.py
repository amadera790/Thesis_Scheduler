from bs4 import BeautifulSoup

idAktWert = 'Courses'
soup = BeautifulSoup(open('AUCS.html'), "html.parser")
a = soup.findAll(id="Courses")    #Note: I have used Index to select the first element in list. 
for i in a:

    print(i.text)