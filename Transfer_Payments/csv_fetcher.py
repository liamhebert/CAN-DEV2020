from bs4 import BeautifulSoup
import wget
import requests
import re
import datetime


url1 = "https://open.canada.ca/data/en/dataset/69bdc3eb-e919-4854-bc52-a435a3e19092"
req = requests.get(url1)
soup = BeautifulSoup(req.text,"lxml")
nowyear = datetime.datetime.now().year
data = req.text

tags = soup.find_all('a')

for year in range(2003,nowyear):
    wget.download("http://donnees-data.tpsgc-pwgsc.gc.ca/ba1/pt-tp/pt-tp-"+str(year)+"-eng.csv")      
