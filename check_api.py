#import mysecrets
import os
import requests
#from urllib.parse import urlparse
import json


def inqUrl(url):
   response = requests.get(url)
   response.encoding = response.apparent_encoding
   jsonData = None
   if(response.text):
       jsonData = json.loads(response.text)
   return jsonData

def addSubscribeMessageToResults(results=[], name='', url='', full=False):
    gitOrg = os.getenv('GITHUB_OWNER')
    results.append("Subscribe to "+name+" API:")
    results.append("1. Login and 'Subscribe to Test' at "+url)
    results.append("2. Make sure to enter 'Start Free Plan' and press 'Subscribe' - **don't** enter credit card data!") 
    results.append(" ")
    if(full):
        results.append("If it doesn't help, **recheck** the registration and the key entry:") 
        results.append("1. Please register at https://rapidapi.com/auth/sign-up")
        results.append("2. Copy your API key from (**X-RapidAPI-Key**) from the [same site]("+url+")")
        results.append("3. Assign the API key as (new?) organization secret or edit it at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions")       
        results.append("   * Name:  **RAPIDAPI_KEY** ")
        results.append("   * Value: **Your key here** ") 
    return True

## NOT WORKING ANY MORE -> TIMEOUT, 0% Service Level!!
def inqRapidFreeNews(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Free-News")
    url = "https://free-news.p.rapidapi.com/v1/search"
    querystring = {"q":"Klimawandel","lang":"de","page":1,"page_size":"20"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "free-news.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.encoding = response.apparent_encoding
    # print(response.text)
    print(response.status_code)     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Free-News respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Free-News")
            addSubscribeMessageToResults(results, "Free-News", "https://rapidapi.com/newscatcher-api-newscatcher-api-default/api/free-news")
            return False
        if (('status' in jsonData) and ('ok'==jsonData['status'])):
          results.append(":white_check_mark: Free-News status fine")
          if (jsonData['total_hits']>0):
            results.append(":white_check_mark: Free-News results found")
            return True
          else: 
            results.append(":no_entry: Free-News results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry:  Free-News status **failed**:")
          addSubscribeMessageToResults(results, "Free-News", "https://rapidapi.com/newscatcher-api-newscatcher-api-default/api/free-news")
          return False
    else:
      results.append(":no_entry: Free-News respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidDeeplTranslator4(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Deepl-Translator-4")
    url = "https://deepl-translator4.p.rapidapi.com/api/v1/translate"
    payload = {"text":"Klimawandel","from":"de","to":"en"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "deepl-translator4.p.rapidapi.com",
        'Content-Type': 'application/json'
        }
    response = requests.post(url, headers=headers, json=payload)
    #response = requests.request('POST', url, headers=headers, json=payload)
    response.encoding = response.apparent_encoding
    #print(response.text)
    print(['Deepl-Translator-4', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Deepl-Translator-4 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Deepl-Translator-4")
            addSubscribeMessageToResults(results, "Deepl-Translator-4", "https://rapidapi.com/wiryaimdx/api/deepl-translator4")
            return False
        if ('text' in jsonData):
          results.append(":white_check_mark: Deepl-Translator-4 status fine")
          if (jsonData['text']):
            results.append(":white_check_mark: Deepl-Translator-4 results found")
            return True
          else: 
            results.append(":no_entry: Deepl-Translator-4 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Deepl-Translator-4 status **failed**:")
          addSubscribeMessageToResults(results, "Deepl-Translator-4", "https://rapidapi.com/wiryaimdx/api/deepl-translator4")
          return False
    else:
      results.append(":no_entry: Deepl-Translator-4 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False


def inqRapidMultiTraductionTranslate(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Multi-Traduction-Translate")
    url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"
    payload = {"q":"Klimawandel","from":"de","to":"en"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "rapid-translate-multi-traduction.p.rapidapi.com",
        'Content-Type': 'application/json'
        }
    response = requests.post(url, headers=headers, json=payload)
    #response = requests.request('POST', url, headers=headers, json=payload)
    response.encoding = response.apparent_encoding
    #print(response.text)
    print(['Multi-Traduction-Translate', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Multi-Traduction-Translate respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Multi-Traduction-Translate")
            addSubscribeMessageToResults(results, "Multi-Traduction-Translate", "https://rapidapi.com/sibaridev/api/rapid-translate-multi-traduction")
            return False
        if (len(jsonData)>0):
          results.append(":white_check_mark: Multi-Traduction-Translate status fine")
          if (jsonData[0]):
            results.append(":white_check_mark: Multi-Traduction-Translate results found")
            return True
          else: 
            results.append(":no_entry: Multi-Traduction-Translate results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Multi-Traduction-Translate status **failed**:")
          addSubscribeMessageToResults(results, "Multi-Traduction-Translate", "https://rapidapi.com/sibaridev/api/rapid-translate-multi-traduction")
          return False
    else:
      results.append(":no_entry: Multi-Traduction-Translate respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False


def inqRapidFreeGoogleTranslator(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Free-Google-Translator")
    url = "https://free-google-translator.p.rapidapi.com/external-api/free-google-translator"
    querystring = {"query":"Klimawandel","from":"de","to":"en"}
    payload = {"translate":"rapidapi"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "free-google-translator.p.rapidapi.com",
        'Content-Type': 'application/json'
        }
    response = requests.post(url, headers=headers, json=payload, params=querystring)
    #response = requests.request('POST', url, headers=headers, json=querystring)
    response.encoding = response.apparent_encoding
    print(response.text)
    print(['Free-Google-Translator', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Free-Google-Translator respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Free-Google-Translator")
            addSubscribeMessageToResults(results, "Free-Google-Translator", "https://rapidapi.com/joshimuddin8212/api/free-google-translator")
            return False
        if ('translateTo' in jsonData):
          results.append(":white_check_mark: Free-Google-Translator status fine")
          if ('translation' in jsonData):
            results.append(":white_check_mark: Free-Google-Translator results found")
            return True
          else: 
            results.append(":no_entry: Free-Google-Translator results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Free-Google-Translator status **failed**:")
          addSubscribeMessageToResults(results, "Free-Google-Translator", "https://rapidapi.com/joshimuddin8212/api/free-google-translator")
          return False
    else:
      results.append(":no_entry: Free-Google-Translator respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidTextTranslator2(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Text-Translator-2")
    url = "https://text-translator2.p.rapidapi.com/translate"
    payload = {"text":"Klimawandel","source_language":"de","target_language":"en"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "text-translator2.p.rapidapi.com",
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    response = requests.post(url, headers=headers, data=payload)
    #response = requests.request('POST', url, headers=headers, json=payload)
    response.encoding = response.apparent_encoding
    #print(response.text)
    print(['Text-Translator-2', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Text-Translator-2 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Text-Translator-2")
            addSubscribeMessageToResults(results, "Text-Translator-2", "https://rapidapi.com/dickyagustin/api/text-translator2")
            return False
        if ('data' in jsonData):
          results.append(":white_check_mark: Text-Translator-2 status fine")
          if ('translatedText' in jsonData['data']):
            results.append(":white_check_mark: Text-Translator-2 results found")
            return True
          else: 
            results.append(":no_entry: Text-Translator-2 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Text-Translator-2 status **failed**:")
          addSubscribeMessageToResults(results, "Text-Translator-2", "https://rapidapi.com/dickyagustin/api/text-translator2")
          return False
    else:
      results.append(":no_entry: Text-Translator-2 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidMicroTranslate3(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Microsoft-Translator-3")
    url = "https://microsoft-translator-text-api3.p.rapidapi.com/translate"
    querystring = {"textType":"plain","from":"de","to":"en"}
    payload = [{"text":"Klimawandel"}]
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "microsoft-translator-text-api3.p.rapidapi.com",
        'Content-Type': 'application/json'
        }
    response = requests.post(url, headers=headers, json=payload, params=querystring)
    #response = requests.request('POST', url, headers=headers, json=querystring)
    response.encoding = response.apparent_encoding
    print(response.text)
    print(['Microsoft-Translator-3', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 502, 504])):
        results.append(":white_check_mark: Microsoft-Translator-3 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Microsoft-Translator-3")
            addSubscribeMessageToResults(results, "Microsoft-Translator-3", "https://rapidapi.com/apiship-apiship-default/api/microsoft-translator-text-api3")
            return False
        if('messages' in jsonData):
          if('The API is unreachable, please contact the API provider'==jsonData['messages']):
            results.append(":no_entry: Microsoft-Translator-3 **not** reachable")
            results.append("Maybe retry later...?") #?
            return False
          print(jsonData['messages'])
        if (len(jsonData)>0):
          results.append(":white_check_mark: Microsoft-Translator-3 status fine")
          if ('translations' in jsonData[0]):
            results.append(":white_check_mark: Microsoft-Translator-3 results found")
            return True
          else: 
            results.append(":no_entry: Microsoft-Translator-3 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Microsoft-Translator-3 status **failed**:")
          addSubscribeMessageToResults(results, "Deep-Translate-1", "https://rapidapi.com/apiship-apiship-default/api/microsoft-translator-text-api3")
          return False
    else:
      results.append(":no_entry: Microsoft-Translator-3 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidDeepTranslate1(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Deep-Translate-1")
    url = "https://free-news.p.rapidapi.com/language/translate/v2"
    payload = {"q":"Klimawandel","source":"de","target":"en"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "deep-translate1.p.rapidapi.com",
        'Content-Type': 'application/json'
        }
    response = requests.post(url, headers=headers, json=payload)
    #response = requests.request('POST', url, headers=headers, json=payload)
    response.encoding = response.apparent_encoding
    #print(response.text)
    print(['Deep-Translate-1', response.status_code])     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Deep-Translate-1 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Deep-Translate-1")
            addSubscribeMessageToResults(results, "Deep-Translate-1", "https://rapidapi.com/gatzuma/api/deep-translate1")
            return False
        if ('data' in jsonData):
          results.append(":white_check_mark: Deep-Translate-1 status fine")
          if ('translations' in jsonData['data']):
            results.append(":white_check_mark: Deep-Translate-1 results found")
            return True
          else: 
            results.append(":no_entry: Deep-Translate-1 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Deep-Translate-1 status **failed**:")
          addSubscribeMessageToResults(results, "Deep-Translate-1", "https://rapidapi.com/gatzuma/api/deep-translate1")
          return False
    else:
      results.append(":no_entry: Deep-Translate-1 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False


def inqRapidNewsApi14(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: News-API-14")
    url = "https://free-news.p.rapidapi.com/v2/search/articles"
    querystring = {"query":"Klimawandel","language":"de","limit":"20"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "news-api14.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.encoding = response.apparent_encoding
    # print(response.text)
    print(response.status_code)     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: News-API-14 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to News-API-14")
            addSubscribeMessageToResults(results, "News-API-14", "https://rapidapi.com/bonaipowered/api/news-api14")
            return False
        if (('success' in jsonData) and jsonData['success']):
          results.append(":white_check_mark: News-API-14 status fine")
          if (jsonData['totalHits']>0):
            results.append(":white_check_mark: News-API-14 results found")
            return True
          else: 
            results.append(":no_entry: News-API-14 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: News-API-14 status **failed**:")
          addSubscribeMessageToResults(results, "News-API-14", "https://rapidapi.com/bonaipowered/api/news-api14")
          return False
    else:
      results.append(":no_entry: News-API-14 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidGoogleNews22(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Google-News-22")
    url = "https://free-news.p.rapidapi.com/v1/search"
    querystring = {"q":"Klimawandel","language":"de","country":"de"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "google-news22.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.encoding = response.apparent_encoding
    # print(response.text)
    print(response.status_code)     #400
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Google-News-22 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Google-News-22")
            addSubscribeMessageToResults(results, "Google-News-22", "https://rapidapi.com/bonaipowered/api/google-news22", True)
            return False
        if (('success' in jsonData) and jsonData['success']):
          results.append(":white_check_mark: Google-News-22 status fine")
          if (('total' in jsonData) and (jsonData['total']>0)):
            results.append(":white_check_mark: Google-News-22 results found")
            return True
          else: 
            results.append(":no_entry: Google-News-22 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry:  Google-News-22 status **failed**:")
          addSubscribeMessageToResults(results, "Google-News-22", "https://rapidapi.com/bonaipowered/api/google-news22", True)
          return False
    else:
      results.append(":no_entry: Google-News-22 respone **failed**") 
      addSubscribeMessageToResults(results, "Google-News-22", "https://rapidapi.com/bonaipowered/api/google-news22", True)
      return False
    return False

def inqRapidGoogleNews25(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Google-News-25")
    url = "https://google-news25.p.rapidapi.com/search"
    querystring = {"keyword":"Klimawandel","language":"de-DE"}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "google-news25.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.encoding = response.apparent_encoding
    # print(response.text)
    print(response.status_code)     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Google-News-25 respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Google-News-25")
            addSubscribeMessageToResults(results, "Google-News-25", "https://rapidapi.com/things4u-api4upro/api/google-news25")
            return False
        if (('status' in jsonData) and jsonData['status']):
          results.append(":white_check_mark: Google-News-25 status fine")
          if (len(jsonData['data'])>0):
            results.append(":white_check_mark: Google-News-25 results found")
            return True
          else: 
            results.append(":no_entry: Google-News-25 results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Google-News-25 status **failed**:")
          addSubscribeMessageToResults(results, "Google-News-25", "https://rapidapi.com/things4u-api4upro/api/google-news25")
          return False
    else:
      results.append(":no_entry: Google-News-25 respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False

def inqRapidRealTimeNews(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI: Real-Time-News-Data")
    url = "https://real-time-news-data.p.rapidapi.com/search"
    querystring = {"query":"Klimawandel","lang":"de","country":"DE","limit":10}
    headers = {
        'x-rapidapi-key': apiKey,
        'x-rapidapi-host': "real-time-news-data.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.encoding = response.apparent_encoding
    # print(response.text)
    print(response.status_code)     #200
    #504 : The request to the API has timed out
    if((response.text) and (not response.status_code in [204, 500, 504])):
        results.append(":white_check_mark: Real-Time-News-Data respone fine")
        text = response.text
        if(not isinstance(text,str)):
            text = text.decode("utf-8")
        jsonData = json.loads(text)
        if('message' in jsonData):
          if('You are not subscribed to this API.'==jsonData['message']):
            results.append(":no_entry: **Not** subscribed to Real-Time-News-Data")
            addSubscribeMessageToResults(results, "Real-Time-News-Data", "https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-news-data")
            return False
        if (('status' in jsonData) and ('OK'==jsonData['status'])):
          results.append(":white_check_mark: Real-Time-News-Data status fine")
          if (len(jsonData['data'])>0):
            results.append(":white_check_mark: Real-Time-News-Data results found")
            return True
          else: 
            results.append(":no_entry: Real-Time-News-Data results **not** found")
            results.append("Maybe retry later...?") #?
            return False
        else:
          results.append(":no_entry: Real-Time-News-Data status **failed**:")
          addSubscribeMessageToResults(results, "Real-Time-News-Data", "https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-news-data")
          return False
    else:
      results.append(":no_entry: Real-Time-News-Data respone **failed**") 
      results.append("Maybe retry later...?") #?
      return False
    return False



def checkRapidAPI(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('RAPIDAPI_KEY')
    results.append("### RapidAPI")
    apiKeyExists = True
    if(apiKey):
      if(apiKey == '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y'):
        apiKeyExists = False
    else:
        apiKeyExists = False      
    if(not apiKeyExists): 
        results.append(":no_entry: RapidAPI key **missing**:")
        results.append("1. Please register at https://rapidapi.com/auth/sign-up")
        results.append("2. Login and 'Subscribe to Test' at https://rapidapi.com/bonaipowered/api/google-news22")
        results.append("3. Make sure to enter 'Start Free Plan' and press 'Subscribe' - **don't** enter credit card data!")
        results.append("2. Copy your API key from (**X-RapidAPI-Key**) from the same site")
        results.append("3. Assign the API key as new organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/new")       
        results.append("   * Name:  **RAPIDAPI_KEY** ")
        results.append("   * Value: **Your key here** ") 
        return False    
    else:
        results.append(":white_check_mark: RapidAPI key exists")
        return True 
    return False

def inqNewsApi(results=[]):
  apiKey = os.getenv('NEWSAPI_KEY')
  url = ('https://newsapi.org/v2/everything?q=Klimawandel&language=de&apiKey='+apiKey)
  response = requests.get(url)
  response.encoding = response.apparent_encoding
  if(response.text):
    results.append(":white_check_mark: NewsAPI respone fine") 
    jsonData = json.loads(response.text)
    if ('ok'==jsonData['status']):
      results.append(":white_check_mark: NewsAPI status fine")
      if(jsonData['totalResults']>0):
         results.append(":white_check_mark: NewsAPI results found")
         return True
      else:
         results.append(":no_entry: NewsAPI results **not** found")
         return False
    else:
      results.append(":no_entry: NewsAPI status **failed**:")
      results.append("Please recheck the API key and its assignment:")
      results.append("1. Please register at https://newsapi.org/register")
      results.append("2. Login and get your API key at https://newsapi.org/account")
      results.append("3. Assign the API key as new organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/new") 
      results.append("   * Name:  **NEWSAPI_KEY** ")
      results.append("   * Value: **Your key here** ")          
      return False
  else:
    results.append(":no_entry: NewsAPI respone failed") 
    results.append("Please recheck the API key and its assignment:")
    results.append("1. Please register at https://newsapi.org/register")
    results.append("2. Login and get your API key at https://newsapi.org/account")
    results.append("3. Assign the API key as new organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/new") 
    results.append("   * Name:  **NEWSAPI_KEY** ")
    results.append("   * Value: **Your key here** ")          
    return False
  return False

def checkNewsApi(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('NEWSAPI_KEY')
    results.append("### NewsAPI")
    apiKeyExists = True
    if(apiKey):
      if(apiKey == '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7'):
        apiKeyExists = False
    else:
        apiKeyExists = False      
    if(not apiKeyExists): 
        results.append(":no_entry: NewsAPI key **missing**:")
        results.append("1. Please register at https://newsapi.org/register")
        results.append("2. Login and get your API key at https://newsapi.org/account")
        results.append("3. Assign the API key as new organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/new")       
        results.append("   * Name:  **NEWSAPI_KEY** ")
        results.append("   * Value: **Your key here** ") 
        return False    
    else:
        results.append(":white_check_mark: NewsAPI key exists")
        inqNewsApi(results) 
        return True 
    return False

def addRegisterGeonamesToResults(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    newGitOrg = gitOrg.replace("-","_")
    results.append("1. Please register with username (i.e.: "+newGitOrg+") at https://www.geonames.org/login")
    results.append("2. Assign the choosen username as new organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/new")       
    results.append("   * Name:  **GEONAMES_KEY** ")
    results.append("   * Value: **Your username here** ") 
    return False

def recheckRegisterGeonamesToResults(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    newGitOrg = gitOrg.replace("-","_")
    results.append("1. Please recheck the username (i.e.: "+newGitOrg+") at https://www.geonames.org/login")
    results.append("2. Modify the organization secret at https://github.com/organizations/"+gitOrg+"/settings/secrets/actions/GEONAMES_KEY")       
    results.append("   * Choose 'enter a new value.'")
    results.append("   * Make sure to enter your username ('Welcome **username**.') - but without the trailing dot!") 
    results.append("   * Save") 
    return False


def inqGeonamesApi(results=[]):
  apiKey = os.getenv('GEONAMES_KEY')
  url = ('http://api.geonames.org/searchJSON?name=Freiburg&country=DE&maxRows=10&username='+apiKey)
  response = requests.get(url)
  response.encoding = response.apparent_encoding
  if(response.text):
    results.append(":white_check_mark: Geonames respone fine") 
    jsonData = json.loads(response.text)
    #print(jsonData)

    if('message' in jsonData):
      if(('credits for demo has been exceeded' in jsonData['message']) or ('user does not exist' in jsonData['message'])):
        results.append(":no_entry: **Not** registered at Geonames")
        addRegisterGeonamesToResults(results)
        return False
      if('invalid user' in status['message']):
        results.append(":no_entry: **Not** registered at Geonames (or invalid)")
        recheckRegisterGeonamesToResults(results)
        return False
      if(('user account not enabled to use the free webservice' in status['message']) or ('Please enable it on your account page' in status['message'])):
        results.append(":no_entry: **Not** enabled at Geonames - enable at https://www.geonames.org/manageaccount ")
        #addRegisterGeonamesToResults(results)
        return False

    if('status' in jsonData):
      status = jsonData['status']
      if('message' in status):
        print(status['message'])
        if(('credits for demo has been exceeded' in status['message']) or ('user does not exist' in status['message'])):
          results.append(":no_entry: **Not** registered at Geonames")
          addRegisterGeonamesToResults(results)
          return False
        if('invalid user' in status['message']):
          results.append(":no_entry: **Not** registered at Geonames (or invalid)")
          recheckRegisterGeonamesToResults(results)
          return False
        if(('user account not enabled to use the free webservice' in status['message']) or ('Please enable it on your account page' in status['message'])):
          results.append(":no_entry: **Not** enabled at Geonames - enable at https://www.geonames.org/manageaccount ")
          #addRegisterGeonamesToResults(results)
          return False

    if ('totalResultsCount' in jsonData):
      results.append(":white_check_mark: Geonames result fine")
      if(jsonData['totalResultsCount']>0):
         results.append(":white_check_mark: Geonames results found")
         return True
      else:
         results.append(":no_entry: Geonames results **not** found")
         return False
    else:
      results.append(":no_entry: Geonames status **failed**:")
      results.append("Please recheck the API key and its assignment:")
      addRegisterGeonamesToResults(results)         
      return False
  else:
    results.append(":no_entry: Geonames respone failed") 
    results.append("Please recheck the API key and its assignment:")
    addRegisterGeonamesToResults(results)       
    return False
  return False


def checkGeonamesApi(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    apiKey = os.getenv('GEONAMES_KEY')
    results.append("### GeonamesAPI")
    apiKeyExists = True
    if(apiKey):
      if(apiKey == 'demo_demo_123'):
        apiKeyExists = False
        print('123')
    else:
        apiKeyExists = False     
        print('no key') 
    if(not apiKeyExists): 
        results.append(":no_entry: Geonames key **missing**:")
        addRegisterGeonamesToResults(results)
        return False    
    else:
        results.append(":white_check_mark: Geonames key exists")
        inqGeonamesApi(results) 
        return True 
    return False


def checkGithubOrganization(results=[]):
    gitOrg = os.getenv('GITHUB_OWNER')
    gitRepo = os.getenv('GITHUB_REPO')
    #print(['Org',gitOrg,'Repo',gitRepo])
    results.append("### Github Organization")
    if(gitOrg):
      orgData = inqUrl('https://api.github.com/users/'+gitOrg)
      #print(orgData)    # check for 'type': 'Organization', 'user_view_type': 'public'
      if(not 'Organization'==orgData['type']):
        results.append(":no_entry: Github Organization **missing**:")   
        results.append("1. Create new organization at https://github.com/account/organizations/new?plan=free")
        results.append("2. Organization name could be i.e.: "+gitOrg+"Org")
        results.append("3. Organization belongs to 'My personal account'")
        results.append("4. No add-ons")
        results.append("5. Accept Terms")
        results.append("6. Fork again - in your new organization!")
        ## REFORK
        return (True, False) 
      else:
        results.append(":white_check_mark: Github Organization exists") 
        orgAssigned = False
        myOrgs = inqUrl('https://api.github.com/users/KMicha/orgs?per_page=100')
        #print(myOrgs) 
        for org in myOrgs:
          if(org['id']==orgData['id']):
            orgAssigned = True
        if(orgAssigned):
          results.append(":white_check_mark: Github Organization assigned") 
          return (True, True)  
        else:
          results.append(":no_entry: Github Organization **not** assigned (or not public):")
          results.append("1. Goto https://github.com/orgs/"+gitOrg+"/people")
          results.append("2. Check if KMicha is listed as Members")
          results.append("3. Else: 'Invite member' KMicha")  
          return (True, True)
    else:
      results.append("No check possible: maybe running locally?") 
      return (False, False)
    return (True, True) 

results=[]
results.append("# BASICS")
(runOnGithub, runInOrganization) = checkGithubOrganization(results)
results.append("\n---\n")
if(runInOrganization):
  checkNewsApi(results)
  results.append("\n---\n")
  checkGeonamesApi(results)
  results.append("\n---\n")
  rapidAPIExists = checkRapidAPI(results)
  results.append("\n---\n")
  if(rapidAPIExists):
    ## NEWS:
    results.append("# NEWS")
    results.append("\n---\n") 
    inqRapidGoogleNews22(results)
    results.append("\n---\n")
    #inqRapidFreeNews(results)
    inqRapidNewsApi14(results)
    results.append("\n---\n")
    inqRapidGoogleNews25(results)
    results.append("\n---\n")
    inqRapidRealTimeNews(results)
    results.append("\n---\n")
    results.append("# TRANSLATE")
    results.append("\n---\n") 
    inqRapidDeepTranslate1(results)
    results.append("\n---\n") 
    inqRapidMicroTranslate3(results)
    results.append("\n---\n") 
    inqRapidTextTranslator2(results)
    results.append("\n---\n") 
    inqRapidFreeGoogleTranslator(results)
    results.append("\n---\n") 
    inqRapidMultiTraductionTranslate(results)
    results.append("\n---\n") 
    inqRapidDeeplTranslator4(results)
    
#print(results)

if(runOnGithub):
  f = open("CHECK.md", "w")
  for res in results:
    f.write(res+"  \n")
  f.close()


