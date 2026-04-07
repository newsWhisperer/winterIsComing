import pandas as pd
import numpy as np

from pathlib import Path
import os.path
import io
#import requests
import glob

import datetime
from dateutil import parser

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
#from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import axes3d, Axes3D
import matplotlib.cm as cm

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

import nltk
nltk.download("stopwords")
german_stop_words = list(stopwords.words('german'))

DATA_PATH = Path.cwd()
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')
if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')


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
    newsDF = newsDF.sort_values(by=['published'], ascending=True)        
    return newsDF 

def getNewsDF():
    files = getNewsFiles()
    newsDF = getNewsDFbyList(files)
    return newsDF         

keywordsColorsDF = pd.read_csv(DATA_PATH / 'keywords.csv', delimiter=',')
topicsColorsDF = keywordsColorsDF.drop_duplicates(subset=['topic'])
invalidTopicDF = pd.DataFrame(data={'keyword':['invalidINVALIDinvalid'], 'language':[topicsColorsDF['language'].min()], 'topic':['Invalid'],'topicColor':['#bbbbbb'],'keywordColor':['#bbbbbb'],'limitPages':[2],'ratioNew':[0.01]})
topicsColorsDF = pd.concat([topicsColorsDF, invalidTopicDF])
print(topicsColorsDF)

newsDf = getNewsDF()
newsDf['title'] = newsDf['title'].fillna('')
newsDf['description'] = newsDf['description'].fillna('')
newsDf['quote'] = newsDf['quote'].fillna('')
newsDf['text'] = newsDf['title'] + ' ' + newsDf['description'] 
print(newsDf)  

# Topics & Keywords
fig = plt.figure(figsize=(12, 6), constrained_layout=True)
gs = gridspec.GridSpec(1, 3, figure=fig)

# Topics 
newsDf0 = pd.merge(newsDf, keywordsColorsDF, how='left', left_on=['keyword'], right_on=['keyword'])
for index, column in newsDf0.iterrows():
  if(column['valid'] < 0.5):
     newsDf0.loc[index,'topic'] = 'Invalid'
print(newsDf0)  

newsDf2 = newsDf[newsDf['valid']>0.5]
newsDf2 = pd.merge(newsDf2, keywordsColorsDF, how='left', left_on=['keyword'], right_on=['keyword'])
#newsDf2 = newsDf0.copy()
print(newsDf2.columns)
topicsDF = newsDf2.groupby('topic').count()
topicsDF = topicsDF.drop(columns = ['topicColor'])
topicsDF = pd.merge(topicsDF, topicsColorsDF, how='left', left_on=['topic'], right_on=['topic'])
topicsDF = topicsDF.sort_values('index', ascending=False)
axTopics = plt.subplot(gs[0,0])
axTopics.set_title("Topics (valid)", fontsize=24)
plot = topicsDF.plot.pie(y='index', ax=axTopics, colors=topicsDF['topicColor'], labels=topicsDF['topic'].str.slice(0,20),legend=False,ylabel='')
#plot = topicsDF.plot(kind='pie', y='index', ax=axKeywords, colors='#'+keywordsDF['keywordColor'])

# Keywords valid
newsDf1 = newsDf[newsDf['valid']>0.5]
##newsDf1 = newsDf0[newsDf0['valid']>0.5]
keywordsDF = newsDf1.groupby('keyword').count()
print(keywordsDF)
keywordsDF = keywordsDF.dropna()
keywordsDF = pd.merge(keywordsDF, keywordsColorsDF, how='inner', left_on=['keyword'], right_on=['keyword'])
keywordsDF = keywordsDF.sort_values('index', ascending=False)
axKeywords = plt.subplot(gs[0,1])
axKeywords.set_title("Keywords (valid)", fontsize=24)
print(keywordsDF)
print(keywordsDF.columns)
plot = keywordsDF.plot.pie(y='index', ax=axKeywords, colors=keywordsDF['keywordColor'], labels=keywordsDF['keyword'].str.slice(0,20),legend=False,ylabel='')
#plot = topicsDF.plot(kind='pie', y='index', ax=axKeywords, colors='#'+keywordsDF['keywordColor'])

# Keywords invalid
newsDf3 = newsDf[newsDf['valid']<0.5]
keywordsDF = newsDf3.groupby('keyword').count()
keywordsDF = keywordsDF.dropna()
keywordsDF = pd.merge(keywordsDF, keywordsColorsDF, how='inner', left_on=['keyword'], right_on=['keyword'])
##topicsDF = topicsDF[topicsDF['valid']>0.5]
keywordsDF = keywordsDF.sort_values('index', ascending=False)
axKeywords = plt.subplot(gs[0,2])
axKeywords.set_title("Keywords (invalid)", fontsize=24)
plot = keywordsDF.plot.pie(y='index', ax=axKeywords, colors=keywordsDF['keywordColor'], labels=keywordsDF['keyword'].str.slice(0,20),legend=False,ylabel='')

plt.savefig(DATA_PATH / 'img' / 'keywords_pie_all.png', dpi=300)
plt.close('all')

#
bayesDF = pd.DataFrame(None) 
if(os.path.exists(DATA_PATH / 'csv' / 'words_bayes_topic_all.csv')):
    bayesDF = pd.read_csv(DATA_PATH / 'csv' / 'words_bayes_topic_all.csv', delimiter=',',index_col='word')
print(bayesDF)


#TFIDF
n_features = 16000
n_components = 19
n_top_words = 20
weighted = False
#lowercase = True
lowercase = False

bayesDF2 = pd.DataFrame(None) 
bayesDict = {}
if(not bayesDF.empty):
    bayesDF2 = bayesDF
    if(lowercase):
       bayesDF2.index = bayesDF2.index.str.lower()
    bayesDF2 = bayesDF2[~bayesDF2.index.duplicated(keep='first')]
    bayesDF2 = bayesDF2[bayesDF2.index.notnull()]
    bayesDict = bayesDF2.to_dict('index')

if(not bayesDF2.empty):
  fig, axes = plt.subplots(4, 5, figsize=(17, 12), sharex=True)
  axes = axes.flatten()
  plt.rcParams.update({'font.size': 6 })
  topic_idx = -1
  ##for topic in reversed(colorsTopics.keys()):

  for index2, column2 in topicsColorsDF.head(n_components).iterrows():
    topic = column2['topic']
    topic_idx += 1
    topicWords = {}  
    topicColor = column2['topicColor']
    topicColors = []
    if(topic in bayesDF2.columns):
      bayesDF2 = bayesDF2.sort_values(by=[topic], ascending=False)
      for index, column in bayesDF2.iterrows():    
        if(len(topicWords) < n_top_words):
            if(index and (type(index) == str) and (column[topic]<100)):    
              #don't use 2grams  
              if(not ' ' in index):      
                topicWords[index] = column[topic]
                topicColors.append(topicColor)
        else:
            break        


    top_features = list(topicWords.keys())
    weights = np.array(list(topicWords.values()))
    bayesColors = topicColor ##extractColors(topicWords)
    bayesTopic = topic ## bayesColors['topic']

    ax = axes[topic_idx]
    ax.barh(top_features, weights, height=0.7, color=topicColors)
    #ax.set_xscale('log')
    ax.set_title((topic + " ("+bayesTopic+")"), fontdict={"fontsize": 9, "horizontalalignment":"right", "color":topicColor})
    ax.invert_yaxis()
    ax.tick_params(axis="both", which="major", labelsize=6)
    for i in "top right left".split():
        ax.spines[i].set_visible(False)
    fig.suptitle("Bayes Topics", fontsize=9)

  plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
  plt.savefig(DATA_PATH / "img" / ("topics_bayes" + ".png"), dpi=300)
  plt.close('all')


def extractColors(words):
    summary = {}
    wordColors = []
    maxTopicValue = -1E20 
    maxTopicColor = '#000000'
    maxTopicName = 'None'
    #for topic in colorsTopics:
    for index2, column2 in topicsColorsDF.iterrows():
        topic = column2['topic']
        summary[topic] = 0.0
    for word in words:
        wordColor = '#000000'
        wordValue = -1E20
        wordWeight = words[word]
        if(word in bayesDict):
            bayes = bayesDict[word]
            #for topic in colorsTopics:  
            for index2, column2 in topicsColorsDF.iterrows():
              topic = column2['topic']
              if(topic in bayes):
                if(bayes[topic] > wordValue):
                    wordValue = bayes[topic]
                    wordColor = column2['topicColor']
                if (weighted):
                  summary[topic] += bayes[topic]*wordWeight
                else:
                  summary[topic] += bayes[topic]
        wordColors.append(wordColor)
    ##for topic in colorsTopics: 
    if(not bayesDF2.empty):
     for index2, column2 in topicsColorsDF.iterrows():
        topic = column2['topic'] 
        if(summary[topic] > maxTopicValue):
            maxTopicValue = summary[topic]
            maxTopicColor = column2['topicColor'] ##colorsTopics[topic]
  
            maxTopicName = topic
    return {'topic':maxTopicName, 'color':maxTopicColor, 'colors': wordColors}


legendHandles = []
##for topic in colorsTopics:
for index2, column2 in topicsColorsDF.iterrows():
    patch = mpatches.Patch(color=column2['topicColor'], label=column2['topic'])
    legendHandles.append(patch)
legendHandles.reverse()   


def plot_top_words(model, feature_names, n_top_words, title, filename='topics'):
    
    if (n_components > 20):
        fig, axes = plt.subplots(4, 10, figsize=(17, 12), sharex=True)
    else:
        fig, axes = plt.subplots(4, 5, figsize=(17, 12), sharex=True)    
    axes.flat[n_components].remove()
    axes = axes.flatten()
    plt.rcParams.update({'font.size': 6 })

    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]
        featDict = dict(zip(top_features,weights))
        bayesColors = extractColors(featDict)
        bayesTopic = bayesColors['topic']
        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7, color=bayesColors['colors'])
        ax.set_xscale('log')
        ax.set_title(f"{bayesTopic}", fontdict={"fontsize": 9, "horizontalalignment":"right", "color":bayesColors['color']})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=6)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=10)

    leg = plt.legend(handles=legendHandles,
        title="Topics",
        loc="center right",
        fontsize=6,
        markerscale=0.7,
        bbox_to_anchor=(1, 0, 2.25, 1.1)
    )
    plt.subplots_adjust(top=0.92, bottom=0.05, wspace=1.20, hspace=0.25)
    plt.savefig(DATA_PATH / "img" / filename, dpi=300)
    plt.close('all')


tfidf_vectorizer = TfidfVectorizer(
    max_df=0.95, min_df=2, max_features=n_features, stop_words=german_stop_words, ngram_range=(1, 1), lowercase=lowercase
)
tfidf = tfidf_vectorizer.fit_transform(newsDf.text)  #all
#tfidf = tfidf_vectorizer.fit_transform(newsDf1.text) #valid only


tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()

model = NMF(
    n_components=n_components,
    random_state=1,
    beta_loss="kullback-leibler",
    solver="mu",
    max_iter=1000,
    #alpha=0.1,
    alpha_W=0.07,
    alpha_H=0.05,
    l1_ratio=0.4,
)
W = model.fit_transform(tfidf)
plot_top_words(
    model,
    tfidf_feature_names,
    n_top_words,
    "Topics in NMF model",
    "topics_nmf.png"
)


tf_vectorizer = CountVectorizer(
    max_df=0.95, min_df=2, max_features=n_features, stop_words=german_stop_words, lowercase=lowercase
)
tf = tf_vectorizer.fit_transform(newsDf.text)         #all
#tf = tf_vectorizer.fit_transform(newsDf1.text)        #valid only

lda = LatentDirichletAllocation(
    n_components=n_components,
    max_iter=5,
    learning_method="online",
    learning_offset=50.0,
    random_state=0,
)
lda.fit(tf)

tf_feature_names = tf_vectorizer.get_feature_names_out()
plot_top_words(lda, tf_feature_names, n_top_words, "Topics in LDA model", "topics_lda.png")

#Sentiments, Counts, Entities

def extractTopPercent(df1, limit=0.95, maxSize=25, counter='count'):
  df1 = df1.sort_values(by=[counter], ascending=False)
  df1['fraction'] = 0.0
  df1['fracSum'] = 0.0
  countAll = df1[counter].sum()
  fracSum = 0.0
  for index, column in df1.iterrows():
      fraction = column[counter]/countAll 
      fracSum += fraction
      df1.loc[index,'fraction'] = fraction
      df1.loc[index,'fracSum'] = fracSum 
  df2 = df1[df1['fracSum']<=limit] 
  df2 = df2.sort_values(counter, ascending=False)
  df3 = df1.select_dtypes(include=['number'])
  ##print(['df3',df3])
  rest = df3[df3['fraction']>limit].sum()
  df2 = df2.head(maxSize)  #todo add to rest...
  newRow = pd.Series(data={counter:rest, 'fraction':rest/countAll, 'fracSum':1.0}, name='Other')
  #df2 = df2.append(newRow, ignore_index=False)
  print(df2[counter])
  #df2 = df2.sort_values([counter], ascending=False)
  return df2  

#Domains
domainsDF = pd.DataFrame(None) 
if(os.path.exists(DATA_PATH / 'csv' / 'sentiments_domains.csv')):
    domainsDF = pd.read_csv(DATA_PATH / 'csv' / 'sentiments_domains.csv', delimiter=',',index_col='domain')
    domainsDF = extractTopPercent(domainsDF, limit=0.90, maxSize=25, counter='counting')
#print(domainsDF)

# Bar Domains
y_pos = np.arange(len(domainsDF['counting']))
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
#colors = filterColors(germanDomains['Unnamed: 0'], colorDomains)
ax.barh(y_pos, domainsDF['counting'], align='center')
ax.set_yticks(y_pos)
ax.set_yticklabels(domainsDF.index, fontsize=36)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Articles', fontsize=36)
plt.xticks(fontsize=36)
ax.set_title("Newspapers", fontsize=48)
plt.tight_layout()
plt.savefig(DATA_PATH / 'img' / 'domains_count.png')
plt.close('all')

#Persons
personsDF = pd.DataFrame(None) 
if(os.path.exists(DATA_PATH / 'csv' / 'sentiments_persons.csv')):
    personsDF = pd.read_csv(DATA_PATH / 'csv' / 'sentiments_persons.csv', delimiter=',' ,index_col='phrase')
    personsDF = extractTopPercent(personsDF, limit=0.75, maxSize=25, counter='count')
print(personsDF)

# Bar Persons
y_pos = np.arange(len(personsDF['count']))
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
#colors = filterColors(germanDomains['Unnamed: 0'], colorDomains)
ax.barh(y_pos, personsDF['count'], align='center')
ax.set_yticks(y_pos)
ax.set_yticklabels(personsDF.index, fontsize=36)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Mentions', fontsize=36)
plt.xticks(fontsize=36)
ax.set_title("Persons", fontsize=48)
plt.tight_layout()
plt.savefig(DATA_PATH / 'img' / 'persons_count.png')
plt.close('all')

#Organizations
orgsDF = pd.DataFrame(None) 
if(os.path.exists(DATA_PATH / 'csv' / 'sentiments_organizations.csv')):
    orgsDF = pd.read_csv(DATA_PATH / 'csv' / 'sentiments_organizations.csv', delimiter=',' ,index_col='phrase')
    orgsDF = extractTopPercent(orgsDF, limit=0.75, maxSize=25, counter='count')
print(orgsDF)

# Bar Organizations
y_pos = np.arange(len(orgsDF['count']))
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
#colors = filterColors(germanDomains['Unnamed: 0'], colorDomains)
ax.barh(y_pos, orgsDF['count'], align='center')
ax.set_yticks(y_pos)
ax.set_yticklabels(orgsDF.index, fontsize=36)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Mentions', fontsize=36)
plt.xticks(fontsize=36)
ax.set_title("Organizations", fontsize=48)
plt.tight_layout()
plt.savefig(DATA_PATH / 'img' / 'organizations_count.png')
plt.close('all')

#Locations
locationsDF = pd.DataFrame(None) 
if(os.path.exists(DATA_PATH / 'csv' / 'sentiments_locations.csv')):
    locationsDF = pd.read_csv(DATA_PATH / 'csv' / 'sentiments_locations.csv', delimiter=',' ,index_col='phrase')
    locationsDF = extractTopPercent(locationsDF, limit=0.75, maxSize=25, counter='count')
print(locationsDF)

# Bar Locations
y_pos = np.arange(len(locationsDF['count']))
plt.rcdefaults()
fig, ax = plt.subplots(figsize=(40, 20))
#colors = filterColors(germanDomains['Unnamed: 0'], colorDomains)
ax.barh(y_pos, locationsDF['count'], align='center')
ax.set_yticks(y_pos)
ax.set_yticklabels(locationsDF.index, fontsize=36)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Mentions', fontsize=36)
plt.xticks(fontsize=36)
ax.set_title("Locations", fontsize=48)
plt.tight_layout()
plt.savefig(DATA_PATH / 'img' / 'locations_count.png')
plt.close('all')


def getDay(dateString):
    timeDate = '1970-01-01'
    pubDate = None
    try:
        pubDate = parser.parse(dateString)
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(dateString)
      except:
        print('date parse error 2')   
    if(pubDate):
        timeDate = pubDate.strftime('%Y-%m-%d')
    return timeDate  

#topics per date
indexTopics = {}
for index, column in newsDf0.iterrows():
    #print(column['keyword'])
    dayDate = getDay(column.published)
    if(not dayDate in indexTopics):
        indexTopics[dayDate] = {}
        for index2, column2 in topicsColorsDF.iterrows():
           indexTopics[dayDate][column2['topic']] = 0
    quote = str(column.text).lower()
    foundTopics = {}
    for index2, column2 in topicsColorsDF.iterrows():
       foundTopics[column2['topic']] = False

    #found by matching Keywords chunks
    for index3, column3 in keywordsColorsDF.iterrows():
      keyword = column3['keyword'].strip("'").lower() 
      anyFound = True
      for key in keyword.split(' '): 
        if(not key in quote):
            anyFound = False
      foundTopics[column3['topic']] = anyFound

    #use found as assigned in search
    for index3, column3 in keywordsColorsDF.iterrows():
      print([column3['keyword'],column['keyword']])
      if(column3['keyword'] == column['keyword']):   
        foundTopics[column3['topic']] = True
        #print("fOUND") 

    #print([column['keyword'], foundTopics[column3['topic']]])
    for index2, column2 in topicsColorsDF.iterrows():
        if(foundTopics[column2['topic']]):
          #indexTopics[dayDate][column2['topic']] += 1
          if(column.valid>0.5):
            indexTopics[dayDate][column2['topic']] += column.valid
          else:
            indexTopics[dayDate]['Invalid'] += 1.0-column.valid

indexTopicsDF = pd.DataFrame.from_dict(indexTopics, orient='index', columns=list(topicsColorsDF['topic']))
indexTopicsDF.to_csv(DATA_PATH / 'csv' / "topics_date.csv", index=True)


#3d Bars -> Topics by Date 
germanTopicsDate = pd.read_csv(DATA_PATH / 'csv' / 'topics_date.csv', delimiter=',')
germanTopicsDate = germanTopicsDate.sort_values(by=['Unnamed: 0'], ascending=True)
xa = []
xl = []
ya = []
yl = []
za = []
ca = []

for idx, column in germanTopicsDate.iterrows():
    p = 0
    #for topic in colorsTopics:
    for index2, column2 in topicsColorsDF.iterrows():
        xa.append(idx) 
        xl.append(column['Unnamed: 0'])
        ya.append(p)  
        yl.append(column2['topic'])
        za.append(column[column2['topic']])
        ca.append(column2['topicColor'])
        p += 1
fig = plt.figure(figsize=(30, 20))
## ax = Axes3D(fig)
## ax = fig.gca(projection='3d')
ax = fig.add_subplot(projection='3d')
#fig.subplots_adjust(left=0, right=1, bottom=0, top=1.5)
ticksx = germanTopicsDate.index.values.tolist()
plt.xticks(ticksx, germanTopicsDate['Unnamed: 0'],rotation=63, fontsize=18)
ticksy = np.arange(1, len(topicsColorsDF)+1, 1)
plt.yticks(ticksy, list(topicsColorsDF['topic']), rotation=-4, fontsize=18, horizontalalignment='left')
ax.tick_params(axis='z', labelsize=18, pad=20)
ax.tick_params(axis='y', pad=20)
ax.set_title("Number of Newspaper Articles covering Topics", fontsize=36, y=0.65, pad=-14)
ax.bar3d(xa, ya, 0, 0.8, 0.8, za, color=ca, alpha=0.6)
ax.view_init(elev=30, azim=-70)
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1.0, 0.7, 0.4, 1]))
colorLeg = list(topicsColorsDF['topicColor'])
colorLeg.reverse()
labelLeg = list(topicsColorsDF['topic'])
labelLeg.reverse()
custom_lines = [plt.Line2D([],[], ls="", marker='.', 
                mec='k', mfc=c, mew=.1, ms=30) for c in colorLeg]
leg = ax.legend(custom_lines, labelLeg, 
          loc='center left', fontsize=16, bbox_to_anchor=(0.75, .48))
leg.set_title("Topics", prop = {'size':20})            
plt.savefig(DATA_PATH / 'img' / 'dates_topics_article_count.png', dpi=300)
plt.close('all')
