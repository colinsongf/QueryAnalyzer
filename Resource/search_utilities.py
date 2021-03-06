# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 09:17:47 2014

@author: javier
"""

import json
import urllib
import urllib2
from sgmllib import SGMLParser
from xgoogle.search import GoogleSearch, SearchError
from textblob import TextBlob
from pymongo import MongoClient


def dbClient():      
      #This function makes a Connection with MongoClient, i.e., \n",
      #creates a MongoClient to the running mongod instance. \n",      
      #Making a Connection with MongoClient\n",
      client = MongoClient('localhost', 27017)
      #Getting a Database
      db = client['aolSearchDB']
      return db      


def getgoogleurl(search,siteurl=False):
    if siteurl==False:
        return 'http://www.google.com/search?q='+urllib2.quote(search)+'&oq='+urllib2.quote(search)
    else:
        return 'http://www.google.com/search?q=site:'+urllib2.quote(siteurl)+'%20'+urllib2.quote(search)+'&oq=site:'+urllib2.quote(siteurl)+'%20'+urllib2.quote(search)


def getgooglelinks(search,siteurl=False):
   #google returns 403 without user agent
   headers = {'User-agent':'Mozilla/11.0'}
   req = urllib2.Request(getgoogleurl(search,siteurl),None,headers)
   site = urllib2.urlopen(req)
   data = site.read()
   site.close()

   #no beatifulsoup because google html is generated with javascript
   start = data.find('<div id="res">')
   end = data.find('<div id="foot">')
   if data[start:end]=='':
      #error, no links to find
      return False
   else:
      links =[]
      data = data[start:end]
      start = 0
      end = 0        
      while start>-1 and end>-1:
          #get only results of the provided site
          if siteurl==False:
            start = data.find('<a href="/url?q=')
          else:
            start = data.find('<a href="/url?q='+str(siteurl))
          data = data[start+len('<a href="/url?q='):]
          end = data.find('&amp;sa=U&amp;ei=')
          if start>-1 and end>-1: 
              link =  urllib2.unquote(data[0:end])
              data = data[end:len(data)]
              if link.find('http')==0:
                  links.append(link)
      return links


def searchByQueryAndURL(query, url):
    links = getgooglelinks(query,url)
    l = []
    for link in links:
        print link
        l.append(link)
    return l
    
    
def insertIntoDB(title, desc, url, tags):
    db = dbClient()
    values = {"title": title, 
          "description" : desc,
          "url" : url,
          "tags" : str(tags)
          }
    resources = db.resources
    resources.insert(values)

def translate(phrase): 
    phrase = phrase.replace("...", " ")
    phrase = phrase.replace("-", " ")
    phrase = phrase.replace("'", " ")
    phrase = phrase.replace("_", " ")
    phrase = phrase.replace(".net", " ")
    phrase = phrase.replace(".asp", " ")
    phrase = phrase.replace(".org", " ")
    phrase = phrase.replace(".", " ")
    phrase = phrase.replace("?", " ")
    phrase = phrase.replace("¿", " ")
    phrase = phrase.replace("!", " ")
    phrase = phrase.replace(";", " ")
    phrase = phrase.replace(":", " ")
    phrase = phrase.replace(",", " ")
    phrase = phrase.replace("|", " ")
    phrase = phrase.replace("/", " ")
    phrase = phrase.replace("(", " ")
    phrase = phrase.replace(")", " ")
    ph = TextBlob(phrase)        
    p_translated = ph.translate(from_lang="es", to='en')
    return p_translated.correct()


def searchByXGoogle(query):
    results = []
    try:
        gs = GoogleSearch(query)
        gs.results_per_page = 100
        results = gs.get_results()
        for res in results:
            _title = res.title.encode("ascii", "ignore")  #.decode('utf-8')
            _desc = res.desc.encode("ascii", "ignore")
            _url = res.url.encode("ascii", "ignore")
            tags_1 = translate(_title)            
            tags_2 = translate(_desc)
            tags  = tags_1 + " " + tags_2            
            print "ORIGINAL:"
            print "Title: \t", _title
            print "Descr: \t", _desc
            print "URL: \t", _url
            print "Tags: \t", tags
            print "-------------------------------------------------------"                      
            insertIntoDB(_title, _desc, _url, tags)
            
    except SearchError, e:
         print "Search failed: %s" % e    
         
    return _title, _desc, _url, tags
        

def showSome(searchfor):
    query = urllib.urlencode({'q': searchfor})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
    search_response = urllib.urlopen(url)
    search_results = search_response.read()
    results = json.loads(search_results)
    data = results['responseData']
    print 'Total results: %s' % data['cursor']['estimatedResultCount']
    hits = data['results']
    print 'Top %d hits:' % len(hits)
    for h in hits: print ' ', h['url']
    print 'For more results, see %s' % data['cursor']['moreResultsUrl']
    print
    for result in data['results']:
        #print result
        title = result['title']
        url = result['url']   # was URL in the original and that threw a name error exception
        content = result['content']
        print "Title:\t ", title
        print "Content:\t ", content
        print "Url:\t ", url
        print
        print

def suggestions(request):
    # -----------------------------------------------------------
    # Enter your phrase here.  Be sure to leave the %s at the end!
    # -----------------------------------------------------------
    base_query = request + " %s"  #This is the base query
    
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for letter in alphabet:
       q = base_query % letter;
       query = urllib.urlencode({'q' : q})
       url = "http://google.com/complete/search?output=toolbar&%s" % query
    
       res = urllib2.urlopen(url)
       parser = PullSuggestions()
       parser.feed(res.read())
       parser.close()
       
       for i in range(0,len(parser.suggestions)):
          print "%s\t%s" % (parser.suggestions[i], parser.queries)


# Define the class that will parse the suggestion XML
class PullSuggestions(SGMLParser):

   def reset(self):
      SGMLParser.reset(self)
      self.suggestions = []
      self.queries = []

   def start_suggestion(self, attrs):
      for a in attrs:
         if a[0] == 'data': self.suggestions.append(a[1])

   def start_num_queries(self, attrs):
      for a in attrs:
         if a[0] == 'int': self.queries.append(a[1])


