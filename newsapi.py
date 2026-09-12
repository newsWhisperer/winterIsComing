import mysecrets
import os
import sys
import math

import pandas as pd

from pathlib import Path
import os.path
import glob

import aiohttp
import asyncio
import requests
from urllib.parse import urlparse
import json
import time
import smtplib
import random
import hashlib
import glob
from difflib import SequenceMatcher

# pip3 install deep-translator
from deep_translator import GoogleTranslator

import datetime
#from datetime import timezone
from dateutil import parser

DATA_PATH = Path.cwd()

dtNow = datetime.datetime.fromtimestamp(int(time.time()), datetime.UTC)
dtLastMonth = datetime.datetime.fromtimestamp(int(time.time())-60*60*24*30, datetime.UTC)

keywordsFields = ["keyword","language","topic","topicColor","keywordColor","limitPages","ratioNew"]
keywordsDF = pd.read_csv(DATA_PATH / 'keywords.csv', delimiter=',')  #,index_col='keyword'
keywordsDF['uniqueString'] = keywordsDF['keyword'] + "_" + keywordsDF['language'] + "_" + keywordsDF['topic']
keywordsDF['crc'] = keywordsDF['uniqueString'].apply(
    lambda x: 
        hashlib.sha256(x.encode()).hexdigest()
)
keywordsDF = keywordsDF.sort_values(by=['ratioNew'], ascending=False)  


def getNewsFiles():
    fileName = './csv/news_????_??.csv'
    files = glob.glob(fileName)
    return files  

def getNewsDFbyList(files):    
    newsDF = pd.DataFrame(None)
    for file in files:
        df = pd.read_csv(file, delimiter=',')
        if(newsDF.empty):
            newsDF = df
        else:
            newsDF = pd.concat([newsDF, df])
    if(not newsDF.empty):
        newsDF = newsDF.sort_values(by=['published'], ascending=True)        
    return newsDF 

def getNewsDF():
    files = getNewsFiles()
    newsDF = getNewsDFbyList(files)
    return newsDF     

newsDf = getNewsDF()

keywordsNewsDF = pd.DataFrame(None) 
if(not newsDf.empty):
  keywordsNewsDF = newsDf.groupby('keyword').count()
  keywordsNewsDF = keywordsNewsDF.drop(columns = ['language'])

'''
newsDf['age'] = newsDf['published'].apply(
    lambda x: 
        datetime.datetime.now(datetime.timezone.utc) - parser.parse(x)
)
'''
keywordsNewsDF2 = pd.DataFrame(None) 
if(not keywordsNewsDF.empty):
  keywordsNewsDF2 = pd.merge(keywordsDF, keywordsNewsDF, how='left', left_on=['keyword'], right_on=['keyword'])
  keywordsNewsDF2['index'] = keywordsNewsDF2['index'].fillna(0)
  keywordsNewsDF2['index'] = keywordsNewsDF2['index'] - keywordsNewsDF2['ratioNew']
  keywordsNewsDF2 = keywordsNewsDF2.sort_values(by=['index'], ascending=True)  

rows20 = int(math.ceil(keywordsNewsDF2.shape[0]/5))
keywordsNewsDF2 = keywordsNewsDF2.head(rows20)
print(keywordsNewsDF2)   

rows20 = int(math.ceil(keywordsDF.shape[0]/5))
keywordsDF3 = keywordsDF.head(rows20)
print(keywordsDF3)


searchWords = dict(zip(keywordsDF.keyword.values, keywordsDF.language.values))

#print(keywordsDF)
#print(searchWords)
#print(keywordsDF.sample() )


stopDomains = ["www.mydealz.de", "www.techstage.de", "www.nachdenkseiten.de", "www.amazon.de", "www.4players.de", "www.netzwelt.de", "www.nextpit.de",
               "www.mein-deal.com", "www.sparbote.de", "www.xda-developers.com" "www.pcgames.de", "blog.google", "www.ingame.de", "playstation.com",
               "www.pcgameshardware.de", "9to5mac.com", "roanoke.com", "billingsgazette.com", "richmond.com", "www.rawstory.com", "slate.com",
               "www.computerbild.de", "www.giga.de", "www.heise.de", "www.chip.de"
                ]


#https://github.com/theSoenke/news-crawler/blob/master/data/feeds_de.txt

                  
def dataIsNotBlocked(data):
    for blocked in stopDomains: 
        if blocked in data['domain']:
            return False
    return True         

#replace/drop: "https://www.zeit.de/zustimmung?url="  

#get url data (inq)  -> check if keyword in title|description    and url equal
#see 'https://www.stern.de/panorama/weltgeschehen/news-heute---ocean-viking--rettet-mehr-als-40-menschen-aus-dem-mittelmeer-30598826.html'


def translateData(data):
   if('de'==data['language']):
       data['de'] = str(data['title']) + '. ' + str(data['description'])
       data['en'] = GoogleTranslator(source='de', target='en').translate(text=data['de'])
       data['la'] = GoogleTranslator(source='de', target='la').translate(text=data['de'])
   if('en'==data['language']):
       data['en'] = str(data['title']) + '. ' + str(data['description'])
       data['de'] = GoogleTranslator(source='en', target='de').translate(text=data['en'])
       data['la'] = GoogleTranslator(source='en', target='la').translate(text=data['en'])
   return(data) 


def tranlateAllInDf(df):
  df['la'] = ''
  df['en'] = ''
  df['de'] = ''
  for index, column in df.iterrows():
     data = translateData(column)
     df.loc[index,'la'] = data['la']
     df.loc[index,'en'] = data['en']
     df.loc[index,'de'] = data['de']
  return df

collectedNews = {}

def addNewsToCollection(data):
    global collectedNews
    pubDate = parser.parse(data['published'])
    fileDate = 'news_'+pubDate.strftime('%Y_%m')+'.csv'
    if(fileDate in collectedNews):
      if(not data['hash'] in collectedNews[fileDate]):
        if(not 'archive' in data):
           data = archiveUrl(data)
        collectedNews[fileDate][data['hash']] = data
        return True
    return False

def storeCollection():
    global collectedNews
    print("Inside store")
    #cols = ['url','valid','domain','title','description','image','published','archive','content','quote','language','keyword']
    cols = ['published', 'keyword', 'domain', 'language', 'valid', 'title', 'description', 'url', 'image', 'archive', 'content', 'quote', 'de', 'en', 'la', 'added']
    for dateFile in collectedNews:
        df = pd.DataFrame.from_dict(collectedNews[dateFile], orient='index', columns=cols)
        df.index = df['url'].apply( lambda x: hashlib.sha256(x.encode()).hexdigest()[:32])   
        df = removeDuplicates(df)
        #df.to_csv(DATA_PATH / dateFile, index=True) 
        if(not os.path.exists(DATA_PATH / 'csv')):
            os.mkdir(DATA_PATH / 'csv')
        print(["store file: ", dateFile])    
        df.to_csv(DATA_PATH / 'csv' / dateFile, index_label='index') 
    collectedNews = {}

# self.randomWordsDF = pd.DataFrame.from_dict(self.randomWords, orient='index', columns=self.randomBase.keys())  
# self.randomWordsDF.to_csv(DATA_PATH / self.category / "csv" / ("words_random_"+str(self.randomSize)+".csv"), index=True)


#https://web.archive.org/save/https://translate.google.com/translate?sl=de&tl=en&u=
#https://web.archive.org/save/https://translate.google.com/translate?sl=de&tl=en&u=https://www.nikos-weinwelten.de/beitrag/weinbau_reagiert_auf_den_klimawandel_abschied_vom_oechsle_hin_zur_nachhaltigkeit/


# https://docs.aiohttp.org/en/stable/client_reference.html
# 
async def saveArchive(saveUrl):
    async with aiohttp.ClientSession() as session:
      async with session.get(saveUrl, timeout=120) as response:
        print("x")   

async def getArchives(urlList):
    async with aiohttp.ClientSession() as session:
      async with session.get(saveUrl) as response:
        print("x")   

def findArchives(articles):
    foundArticles = []
    for article in articles:
        data = extractData(article, language, keyWord) 
        if (dataIsNotBlocked(data)):
            a=1

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def removeDuplicates(df1):
    df1['md5'] = ''
    df1['group'] = ''
    df1['similarity'] = 0.0
    df1 = df1.sort_values(by=['published'], ascending=True)

    for index, column in df1.iterrows():
        quote = str(column['domain']) + ' ' + str(column['title']) + ' ' + str(column['description'])
        md5 = hashlib.md5(quote.encode('utf-8')).hexdigest()
        df1.loc[index,'md5'] = md5
        day = '1970-01-01'
        if(len(str(column['published']))>5):
          pubDate = parser.parse(column['published'])
          day = pubDate.strftime('%Y-%m-%d')
         
        groupTxt = str(column['domain']) +  ' ' + day
        group = hashlib.md5(groupTxt.encode('utf-8')).hexdigest()  
        df1.loc[index,'group'] = group

    df1 = df1[~df1.md5.duplicated(keep='first')]  

    for index1, column1 in df1.iterrows():
        quote1 = str(column1['title']) + ' ' + str(column1['description']) 
        df2 = df1[df1['group']==column1['group']]
        for index2, column2 in df2.iterrows():
            if(column1['md5']>column2['md5']):
                quote2 = str(column2['title']) + ' ' + str(column2['description'])
                similarity = similar(quote1,quote2)
                if(similarity > df1.loc[index1,'similarity']):
                    df1.loc[index1,'similarity'] = similarity

    df3 = df1[df1['similarity']<0.8]
    df3 = df3.drop(columns=['md5', 'group', 'similarity'])
    #df3 = df3.sort_values(by=['published'], ascending=True)
    df3 = df3.sort_values(by=['added','valid','published'], ascending=True)
    return df3

def archiveUrl(data):
    #timetravelDate = datetime.datetime.strptime(data['published'], '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d')
    #pubDate = datetime.datetime.fromisoformat(data['published'])
    #pubDate = parser.isoparse(data['published'])
    timetravelDate = '19700101'
    pubDate = None
    try:
        pubDate = parser.parse(data['published'])
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(data['published'])
      except:
        print('date parse error 2')   
    if(pubDate):
        timetravelDate = pubDate.strftime('%Y%m%d')
    #timetravelUrl = 'http://timetravel.mementoweb.org/api/json/'+timetravelDate+'/'+data['url']
    timetravelUrl = 'http://archive.org/wayback/available?url='+data['url']+'&timestamp='+timetravelDate
    try:
        print(["try request", timetravelUrl])
        page = requests.get(timetravelUrl, timeout=60)
        if page.status_code == 200:
            content = page.content
            print(content)
            if(content):
                #print(content)
                jsonData = json.loads(content)
                if(jsonData and ('archived_snapshots' in jsonData)):
                  snapshots = jsonData['archived_snapshots']
                  if('closest' in snapshots):
                    closest = snapshots['closest']
                    if('200'==closest['status']):
                      data['archive'] = closest['url']
                      if('1970-01-01T00:00:00' == data['published']):
                        ts = closest['timestamp']
                        tsNew = ts[0:4]+'-'+ts[4:6]+'-'+ts[6:8]+'T'+ts[8:10]+':'+ts[10:12]+':'+ts[12:14]
                        print(['new ts',ts,tsNew])
                        data['published'] = tsNew
    except:
#    except Exception as e:    
#    except json.decoder.JSONDecodeError as e:    
#    except requests.exceptions.RequestException as e:  
        e = sys.exc_info()[0]
        print("not archived yet")
        saveUrl = 'https://web.archive.org/save/' + data['url'] # archive.org
        #saveUrl = 'https://archive.is/submit/'
        #saveUrl = 'https://archive.ph/submit/'

        ##  pip3 install aiohttp
        try:
           loop = asyncio.get_event_loop()
           loop.run_until_complete(saveArchive(saveUrl))
        except:
           e2 = sys.exc_info()[0]
           print("something more went wrong (timeout/redirect/...)")            

        #async with aiohttp.ClientSession() as session:
        #    async with session.get(saveUrl) as response:
        #        print(await response.status())        
        '''
        try:
            page = requests.get(saveUrl, timeout=240)  # archive.org
            #page = requests.post(saveUrl, data = {'url':data['url']}, timeout=240)
            if page.status_code == 200:
                print('archived!')
        except requests.exceptions.RequestException as e2:
            print("not archivable: " + data['url'])
        '''    
    return data 

def extractData(article, language, keyWord):
    title = article['title']
    description = article['description']
    url = article['url']
    #later use list...
    url = url.replace('https://www.zeit.de/zustimmung?url=', '')
    url = url.replace('%3A', ':')
    url = url.replace('%2F', '/')                
    domain = urlparse(url).netloc
    image = None
    if('urlToImage' in article): 
        image = article['urlToImage']

    published = '1970-01-01T00:00:00'
    if('publishedAt' in article):    
        published = article['publishedAt']
    content = article['content']
    hashStr = hashlib.sha256(url.encode()).hexdigest()[:32]
    data = {'url':url, 'valid':0, 'domain':domain,'published':published, 'description':description, 'title':title, 
            'image':image, 'content':content, 'quote':'', 'language': language, 'keyword':keyWord, 'hash':hashStr, 'added':str(dtNow)}
    return data  

def checkKeywordInQuote(keyword, quote, case=True, anyKey=False):
    allKeywords = []
    anyKeywords = []
    noneKeywords = []
    keyword = keyword.strip("'")
    if(not case):
      keywords = keyword.lower()
      quote = quote.lower()
    keywords = keyword.split(" ")  
    for keyw in keywords:
       if('+' in keyw):
          allKeywords.append(keyw.replace("+",""))
          anyKeywords.append(keyw.replace("+",""))
       elif('-' in keyw):
          noneKeywords.append(keyw.replace("-",""))
       elif(anyKey):
          anyKeywords.append(keyw)
       else:
          allKeywords.append(keyw)
          anyKeywords.append(keyw)
    found = False
    for keyw in anyKeywords:
       found = found or (keyw in quote)   
    for keyw in allKeywords:
       found = found and (keyw in quote)  
    for keyw in noneKeywords:
       found = found and (not keyw in quote)  
    return found

def checkKeywordInQuoteOld(keyword, quote, case=True, anyKey=False):
    keyword = keyword.replace("+","").replace("-","")
    keywords = keyword.strip("'").split(" ")
    if(not case):
        keywords = keyword.strip("'").lower().split(" ")
        quote = quote.lower()
    if(anyKey):
      allFound = False
      for keyw in keywords:
        allFound = allFound or (keyw in quote)    
    else:
      allFound = True
      for keyw in keywords:
        allFound = allFound and (keyw in quote)  

    return allFound

def checkArticlesForKeywords(articles, keywordsDF, seldomDF, language, keyWord):
    keywordsLangDF = keywordsDF[keywordsDF['language']==language]
    foundArticles = []
    for article in articles:
      data = extractData(article, language, keyWord)
      searchQuote = str(data['title']) + " " + str(data['description'])
      fullQuote = str(data['content'])
      foundKeywords = []
      found = False
      valid = 0.1
      for index2, column2 in keywordsLangDF.iterrows(): 
         keyword = column2['keyword']
         if(keyword.strip("'") in searchQuote):
             foundKeywords.append(keyword) 
             found = True
             valid = max(valid,0.9)
         allFound = checkKeywordInQuote(keyword, searchQuote, case=True)
         if(allFound):
             foundKeywords.append(keyword) 
             found = True
             valid = max(valid,0.8)
         allFound = checkKeywordInQuote(keyword, searchQuote, case=False)
         if(allFound):
             foundKeywords.append(keyword) 
             found = True
             max(valid,0.7)
      # add seldom keywords twice if
      keywordsSeldomLangDF = seldomDF[seldomDF['language']==language]
      for index2, column2 in keywordsSeldomLangDF.iterrows(): 
         keyword = column2['keyword']
         allFound = checkKeywordInQuote(keyword, searchQuote, case=True) 
         if(allFound):
             foundKeywords.append(keyword) 
             found = True
      if(not found):
        for index2, column2 in keywordsLangDF.iterrows(): 
           allFound = checkKeywordInQuote(keyword, fullQuote, case=True)
           if(allFound):
             foundKeywords.append(keyword) 
             found = True
             max(valid,0.6) 
      if(not found):
        for index2, column2 in keywordsLangDF.iterrows(): 
           allFound = checkKeywordInQuote(keyword, fullQuote, case=True, anyKey=True)
           if(allFound):
             foundKeywords.append(keyword) 
             found = True
             max(valid,0.2) 
      data['valid'] = valid
      if(valid>0.15):
        foundKeywords.append(keyWord) 
        data['keyword'] = random.choice(foundKeywords)
        foundArticles.append(data)
      else:
        data['keyword'] = keyWord
        #foundArticles.append(data)

    return foundArticles

def filterNewAndArchive(articles, language, keyWord):
    global collectedNews
    newArticles = []
    startTime = time.time()
    for data in articles:
        ##data = extractData(article, language, keyWord) 
        if (dataIsNotBlocked(data)):
            pubDate = parser.parse(data['published'])
            fileDate = 'news_'+pubDate.strftime('%Y_%m')+'.csv'
            if(not fileDate in collectedNews):
                if(os.path.isfile(DATA_PATH / 'csv' / fileDate)):
                    df = pd.read_csv(DATA_PATH / 'csv' / fileDate, delimiter=',',index_col='index')
                    if(not 'added' in df.columns):
                      df['added'] = str(dtLastMonth)
                    if(not 'la' in df.columns):
                      df = tranlateAllInDf(df)
                    collectedNews[fileDate] = df.to_dict('index')
                else:
                    collectedNews[fileDate] = {}
            if(not data['hash'] in collectedNews[fileDate]):
                data = archiveUrl(data)
                data = translateData(data)
                newArticles.append(data)
        if((time.time() - startTime) > 60*10):
            return newArticles        
    return newArticles

def getNewsFiles(state='harvest'):
    fileName = './csv/news_????_??.csv'
    if(state):
        fileName = './csv/news_'+state+'_????_??.csv'
    files = glob.glob(fileName)
    return files  

def getLatestFileAge():
    minAge = 1E6
    now = time.time()
    for fileName in getNewsFiles(state=None):
        print([os.path.getatime(fileName),os.path.getctime(fileName),os.path.getmtime(fileName)])
        modifyDate = os.path.getmtime(fileName)
        fileAge = now-modifyDate
        print(fileAge)
        if(fileAge<minAge):
            minAge = fileAge
    return minAge        


def inqRandomNews():
    apiKey = os.getenv('NEWSAPI_KEY')
    if(apiKey == '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7'): 
        print('Please set newsapi.org key in file: mysecrets.py');
        return None


    rndKey = keywordsDF.sample()
    randomNumber = random.random()
    if(keywordsDF3.ratioNew.max()>0.8):
      randomNumber = 0.05 

    print(['randomNumber: ',randomNumber])
    if(not keywordsNewsDF2.empty):
      if(randomNumber>0.8):
        print("DF2 seldoms")
        rndKey = keywordsNewsDF2.sample()
    if(not keywordsDF3.empty):
      if(randomNumber<0.4): 
        print("DF3 successors")
        rndKey = keywordsDF3.sample()
    #if FoundAny: newLimit = minimum(currPage+1,limitPage)
    #if foundNothing:  newLimit = maximum(1,random.choice(range(currPage-1,limitPage-1)))

    ## cheat for now!     
    ### keywordEmptyDF = keywordsDF[keywordsDF['keyword']=="'Gasheizung'"]
    ### rndKey = keywordEmptyDF.sample()
    ## rm in final version

    #keyWord = random.choice(searchWords)
    #language = 'de'
    #language = 'en'   
    #language = 'fr' 
    crc = rndKey['crc'].iloc[0]
    keyWord = rndKey['keyword'].iloc[0]
    language = rndKey['language'].iloc[0]
    limitPages = rndKey['limitPages'].iloc[0]
    ratioNew = rndKey['ratioNew'].iloc[0]
    currPage = random.choice(range(1,limitPages+1))  
    newLimit = max(1,random.choice(range(currPage-1,limitPages)))
    currRatio = ratioNew
          
    print([keyWord, language])
    if(not 'xx'==language):
        sort = random.choice(['relevancy', 'popularity', 'publishedAt'])
        pageSize = 33
        print('keyword: '+keyWord+'; Page: '+str(currPage))
        # https://newsapi.org/docs/endpoints/everything
        url = ('https://newsapi.org/v2/everything?'+
            #'q="'+keyWord+'"&'
            'q='+keyWord+'&'
            'pageSize='+str(pageSize)+'&'
            'language='+language+'&'
            'page='+str(currPage)+'&'
            'sortBy='+sort+'&'
            'apiKey='+apiKey
            #'excludeDomains=www.zeit.de,www.reuters.com'
            )
        print(['query', 'q='+keyWord+'&'])    
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        
        foundNew = False
        if(response.text):
            jsonData = json.loads(response.text)
            if ('ok'==jsonData['status']):
             currRatio = 0
             if(jsonData['totalResults']>0):
              currRatio = jsonData['totalResults']/1E7
              if(len(jsonData['articles']) > 0):
                currRatio += len(jsonData['articles'])/1E3
                deltaLimit = 0
                #newLimit = limitPages
                if(len(jsonData['articles']) > 20):
                  deltaLimit += 1  
                  #newLimit = max(currPage+1,limitPages)                
                print('#found Articles: '+str(len(jsonData['articles'])))
                checkedArticles = checkArticlesForKeywords(jsonData['articles'], keywordsDF, keywordsNewsDF2,language, keyWord)
                print('#checked Articles: '+str(len(checkedArticles)))
                print("archive first")
                newArticles = filterNewAndArchive(checkedArticles, language, keyWord)
                print('#new Articles: '+str(len(newArticles)))
                 
                if(len(newArticles) in [1,2]):     
                    print("sleep")   
                    time.sleep(60)
                print("add to collection")
                ##currRatio += len(newArticles)/len(jsonData['articles'])
                for oneArticle in newArticles:
                  currRatio += oneArticle['valid']/len(jsonData['articles'])
                if(currRatio>0.5):
                    deltaLimit += 1
                    #newLimit = max(currPage+2,limitPages)
                newLimit =  min(3,max(currPage+deltaLimit,limitPages))
                print(['currRatio',currRatio,'currPage: ',currPage,' limitPages: ',limitPages,' deltaLimit: ',deltaLimit,' new Limit: ', newLimit])  

                for data in newArticles:
                    if (dataIsNotBlocked(data)):                    
                        #print(str(keyWord)+': '+str(title)+' '+str(url))
                        print(["addNewsToCollection: ",data])
                        if(addNewsToCollection(data)):
                            foundNew = True
                            print(["+++added"])  
                        else:
                            print(["---not added"])    
                #print(["collectedNews: ",collectedNews])            
                if(foundNew):         
                    storeCollection()
            else:
              print(response.text)
              if(jsonData['code'] == 'maximumResultsReached'):
                deltaLimit = -1
                newLimit =  max(1,currPage+deltaLimit)
              # {"status":"error","code":"maximumResultsReached","message":"You have requested too many results. Developer accounts are limited to a max of 100 results. You are trying to request results 100 to 150. Please upgrade to a paid plan if you need more results."}
    #print(rndKey.index)
    #keywordsDF.at[rndKey.index, 'limitPages'] = newLimit    
    keywordsDF.loc[keywordsDF['crc'] == crc, 'limitPages'] = newLimit 
    keywordsDF.loc[keywordsDF['crc'] == crc, 'ratioNew'] = currRatio*0.15+ratioNew*0.85
        
      

#b'{"status":"ok","totalResults":1504,
# "articles":[{"source":{"id":null,"name":"heise online"},
#              "author":"Stefan Krempl",
#              "title":"Wissenschaftler: Klimawandel tr\xc3\xa4gt zum Starkregen bei\xe2\x80\x8b",
#              "description":"Die Wolkenbr\xc3\xbcche mit katastrophalen Folgen geh\xc3\xb6ren so nicht mehr zur \xc3\xbcblichen Wetter-Varianz, meinen Wissenschaftler. Sie fordern einen Umbau der Infrastruktur.",
#              "url":"https://www.heise.de/news/Wissenschaftler-Klimawandel-traegt-zum-Starkregen-bei-6140856.html",
#              "urlToImage":"https://heise.cloudimg.io/bound/1200x1200/q85.png-lossy-85.webp-lossy-85.foil1/_www-heise-de_/imgs/18/3/1/3/9/7/8/0/Ueberschwemmung-c06f751f2932e14b.jpeg",
#              "publishedAt":"2021-07-16T15:06:00Z",
#              "content":"Nach den langen und heftigen Regenf\xc3\xa4llen Mitte der Woche treten immer mehr katastrophale Folgen zutage: Die Zahl der Toten w\xc3\xa4chst, allein in Rheinland-Pfalz und Nordrhein-Westfalen sind \xc3\xbcber 100 Mens\xe2\x80\xa6 [+4840 chars]"}

'''
#time.sleep(80000)
i=1
while True:
###while (i<50):    
  print(i)  
  inqRandomNews()
  i += 1
  #time.sleep(200) # unless drop none-french
  #time.sleep(20)
  time.sleep(1000)

age = getLatestFileAge()
print(age)
if(age>60*60*5*0):
    inqRandomNews()
'''
inqRandomNews()

#keywordsDF = keywordsDF.sort_values(by=['topic','keyword'])
keywordsDF = keywordsDF.sort_values(by=['ratioNew'], ascending=False)
keywordsDF.to_csv(DATA_PATH / 'keywords.csv', columns=keywordsFields,index=False)  

'''
i=1
while True:
###while (i<50):    
  print(i)  
  inqRandomNews()
  i += 1
  #time.sleep(200) # unless drop none-french
  #time.sleep(20)
  keywordsDF = keywordsDF.sort_values(by=['ratioNew'], ascending=False)
  keywordsDF.to_csv(DATA_PATH / 'keywords.csv', columns=keywordsFields,index=False) 
  time.sleep(1000)
'''    
