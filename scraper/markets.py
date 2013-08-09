# -*- coding: utf-8 -*-
import re
from datetime import datetime
import decimal
import mechanize
from lxml import etree
from urlparse import urlparse, parse_qs
from StringIO import StringIO
import logging
import os
import requests
import requests_cache
import sys,os
from scraper.scrapelib import TreeScraper


_here=os.path.split(__file__)[0]
if not _here in sys.path:
	sys.path.append(_here) 


from scraper.browser import browser


logger=logging.getLogger(os.path.split(__file__)[0])

# from topapps.settings import PUBLISHER_BLACKLIST

class NoAppLinkException(Exception):

     def __init__(self, msg):
        self.msg = msg

     def __unicode__(self):
         return repr(self.msg)

def cast_as_float(string):
    result = re.sub(r'[^0-9,\.]','',string)
    result = re.sub(r',','.',result)
    try :
    	return round(float(result),2)
    except ValueError :
	return string

def check_is_banned(string):
   # if string:
   #     for pattern in PUBLISHER_BLACKLIST:
   #         if re.search(pattern, string, re.I | re.M):
   #             return True
    return False

class Extractor(object):

    def __init__(self, tree, url):
        self.tree = tree
        self.url = url
        self.xtitle = None
        self.xshortdesc = None
        self.xlongdesc = None
        self.xpublisher = None
        self.xscreenshots = None

    def _do_xpath(self, xpath, default='', listed=None):
        result = default
        if xpath:
            elem = self.tree.xpath(xpath)
            len_elem = len(elem)
            if len_elem:
                if listed:
                    result = listed.join([e.text for e in elem])
                elif type(elem[0]) in [etree._ElementStringResult, etree._ElementUnicodeResult]:
                    result = " ".join(elem) if len_elem > 1 else elem[0]
                elif hasattr(elem[0], 'text'):
                    result = elem[0].text
            if result is None:
                result = default
        return result.strip()

    def getDescription(self) :
	return ""

    def getTitle(self):
        return self._do_xpath(self.xtitle, 'Title')

    def getMarketDesc(self):
        return self._do_xpath(self.xmarketdesc, 'Marketdesc')

    def getPublisher(self):
        publisher = self._do_xpath(self.xpublisher, 'Publisher')
        return publisher.replace('von ','')

    def getCost(self):
        price = self._do_xpath(self.xcost)
        price = price.replace('Kostenlos','')
        price = price.replace('Free','')
        return cast_as_float(price) if price else 0.0

    def getIcon(self):
        return self._do_xpath(self.xicon)

    def getUpdated(self):
        return self._do_xpath(self.xupdated)

    def getCategory(self):
        return self._do_xpath(self.xcategory)

    def getVersion(self):
        return self._do_xpath(self.xversion) if self.xversion else ''

    def getRequired(self):
        return re.sub(r'( oder h\xf6her|Kompatibel mit )','', self._do_xpath(self.xrequired)) if self.xrequired else ''

    def getRating(self):
        rating = self._do_xpath(self.xrating) if self.xrating else ''
        if rating:
            rating = cast_as_float(rating)
        return  rating

    def getAppId(self):
        return None

    def getResource1(self, app_id):
        return self.url

    def getResource2(self, app_id):
        return None

    def getLanguage(self):
        return self._do_xpath(self.xlanguage) if self.xlanguage else ''

    def getScreenshots(self):
        screenshots = []
        elem = self.tree.xpath(self.xscreenshots) if self.xscreenshots else []
        if len(elem):
            screenshots = [img.attrib.get('src') for img in elem]
        return screenshots
    

class AndroidExtractor(Extractor):

    def __init__(self, tree, url):
        super(AndroidExtractor, self).__init__(tree, url)
        self.xtitle = '//div[@class="doc-metadata"]/dl[@class="doc-metadata-list"]/span[@itemprop="name"]/@content'
        self.xmarketdesc = '//div[@id="doc-original-text"]//text()'
        self.xpublisher = '//span[@itemtype="http://schema.org/Organization" and @itemprop="author"]/span[@itemprop="name"]/@content'
        self.xcost = '//dd[@itemtype="http://schema.org/Offer" and @itemprop="offers"]/span[@itemprop="price"]/@content'
        self.xicon =  '//div[@class="doc-banner-icon"]/img/@src'
        self.xupdated = '//dd/time[@itemprop="datePublished"]'
        self.xcategory ='//span[@itemtype="http://data-vocabulary.org/Breadcrumb" and position()=3]/a[@itemprop="url"]/span[@itemprop="title"]'
        self.xversion ='//dl/dd[@itemprop="softwareVersion"]'
        self.xrequired ='//dt[@content="Android" and @itemprop="operatingSystems"]/following-sibling::*[1]'
        self.xrating = '//dd[@itemtype="http://schema.org/AggregateRating"]/div[@itemprop="ratingValue"]/@content'
        self.xlanguage = ''
        self.xscreenshots = '//div[@class="doc-overview-screenshots"]//div[@class="screenshot-carousel-content-container"]/div[not(@data-baseurl="")]'

    def getAppId(self):
        u = urlparse(self.url)
        if u.query:
            params = parse_qs(u.query).get('id')
            if params:
                return params[0]
        return None

    def getResource1(self, app_id):
        return 'https://play.google.com/store/apps/details?id='+app_id

    def getResource2(self, app_id):
        return 'market://details?id='+app_id

    def getUpdated(self):
        abbr = {u'Januar': '01',u'Februar': '02',u'März': '03',
            u'April': '04',u'Mai': '05',u'Juni': '06',
            u'Juli': '07',u'August': '08',u'September': '09',
            u'Oktober': '10',u'November': '11',u'Dezember': '12',}
        updated = self._do_xpath(self.xupdated)
        for a in  [m for m in abbr if updated.find(m) > -1]:
            updated = updated.replace(' %s ' % a, '%s.' % abbr[a])
        return updated

    def getScreenshots(self):
        screenshots = []
        elem = self.tree.xpath(self.xscreenshots) if self.xscreenshots else []
        if len(elem):
            screenshots = [e.attrib.get('data-baseurl') for e in elem]
        return screenshots

class WindowsExtractor(Extractor):

    def __init__(self, tree, url):
        super(WindowsExtractor, self).__init__(tree, url)
        self.xtitle = '//div[@id="application"]/h1'
        self.xmarketdesc = '//div[@id="appDetails"]/div[@id="appDescription"]/div[@class="description"]/pre'
        self.xpublisher = '//div[@id="publisher"]/a'
        self.xcost = '//div[@itemtype="http://schema.org/Offer" and @itemprop="offers"]/span[@itemprop="price"]'
        self.xicon =  '//div[@id="appSummary"]/div/img[@itemprop="image"]/@src'
        self.xupdated = '//div[@id="releaseDate"]/meta[@itemprop="datePublished"]/@content'
        self.xcategory ='//strong[@itemprop="applicationCategory"]'
        self.xversion ='//span[@itemprop="softwareVersion"]'
        self.xrequired ='//div[@id="softwareRequirements"]/ul/li[@itemprop="operatingSystems"]'
        self.xrating = '//div[@id="rating"]/div/@class'
        self.xlanguage = '(//div[@id="languages"]/ul/li)|(//div[@id="singlelanguage"])'
        self.xscreenshots = '//div[@id="screenshots"]/ul/li/a/img'
		

    def getAppId(self):
        parts = self.url.split('/')
        id_list = [p for p in parts if re.match(r'([a-z0-9]{4,15}-?){5}', p)]
        if id_list:
            return id_list[0]
        return None

    def getResource1(self, app_id):
        return 'http://www.windowsphone.com/s?appid='+app_id

    def getResource2(self, app_id):
        return self.url

    def getLanguage(self):
        langs = self._do_xpath(self.xlanguage, listed=", ")
        return langs

    def getRating(self):
        try:
            elem = self.tree.xpath(self.xrating)
            points = {'zero': 0.0, 'one': 1.0, 'two': 2.0,'three': 3.0,
                'four': 4.0, 'five': 5.0}
            if elem:
                digits = elem[0].split(' ')[1].lower().split('pt')
                return points.get(digits[0],0)+(points.get(digits[1],0)/10)
        except:
            pass
        return ''

    def getRequired(self):
        return self._do_xpath(self.xrequired, listed=", ")
    
    def getScreenshots(self):
        screenshots = []
        elem = self.tree.xpath(self.xscreenshots) if self.xscreenshots else []
        if len(elem):
            screenshots = [a.attrib.get('href') for a in elem]
        return screenshots
    

class IphoneExtractor(Extractor):

    def __init__(self, tree, url):
        super(IphoneExtractor, self).__init__(tree, url)
        self._treescraper=None
        self.xtitle = '//div[@id="title"]//h1'
        self.xmarketdesc = '//div[@class="product-review" and position() = 1]/p/text()'
        self.xpublisher = '//div[@id="title"]//h2'
        self.xcost = '//ul[@class="list"]/li/div[@class="price"]'
        self.xicon ='//div[@id="left-stack"]/div/a/div/img/@src'
        self.xupdated = '//ul[@class="list"]/li[@class="release-date"]/text()'
        self.xcategory ='//li[@class="genre"]/a'
        self.xversion = '//div[@id="left-stack"]/div/ul[@class="list"]/li[4]/text()'
        self.xrequired ='//div[@id="left-stack"]/div/p/text()'
        self.xrating = '//div[@id="left-stack"]//div[@class="rating"]/div[position() = 1]/span'
        self.xlanguage = '//div[@id="left-stack"]/div/ul/li[@class="language"]/text()'
        self.xscreenshots = '//div[@class="lockup"]/img'
        self.xdescription = '//div[@class="product-review"]//p/text()'
    

    def getDescription(self):
        try:
            elem = self.tree.xpath(self.xdescription)
	    return "".join(elem)
	except Exception, e:
	    return ""

    def getAppId(self):
        match = re.match(r'.*/id([0-9]+)[^0-9]*', self.url)
        if match:
            return match.groups(0)[0]

    def getRating(self):
        try:
            elem = self.tree.xpath(self.xrating)
            points = {'': 1, 'half':0.5}
            if len(elem) > 5:
                ratings = [points.get(e.get('class').replace('rating-star','').strip(),0) for e in elem[0:5]]
                return float(sum(ratings))
        except:
            pass
        return ''
        
        
    def getPurchases(self) :
    	t=self.getTreeScraper()
    	return t.extract("div.in-app-purchases li",price="./span[@class='in-app-price']/text()",title="./span[@class='in-app-title']/text()")

    def getRatings(self) :
    	t=self.getTreeScraper()
    	return t.extract("//div[@class='extra-list customer-ratings']//div/@aria-label")
	
    def getTreeScraper(self,html=None) :
    	if html and not self._treescraper :
    		self._treescraper=TreeScraper(html)
    	return self._treescraper

class NokiaExtractor(Extractor):

    def __init__(self, tree, url):
        super(NokiaExtractor, self).__init__(tree, url)
        self.xtitle = '//div[@class="contentDescription item"]/h1[@class="title fn"]'
        self.xmarketdesc = '//div[@class="contentDescription item"]/p[@itemprop="description"]/text()'
        self.xpublisher = '//span[@itemprop="author"]/a[@itemprop="name"]'
        self.xcost = '//div[@itemtype="http://schema.org/Offer" and @itemprop="offers"]/meta[@itemprop="price"]/@content'
        self.xicon = ''
        self.xupdated = ''
        self.xcategory ='//ul[@id="breadcrumb"]/li[position() = "3"]/a'
        self.xversion = ''
        self.xrequired =''
        self.xrating = '//div[@class="contentDescription item"]/span[@itemprop="aggregateRating"]/p[@itemprop="ratingValue"]'
        self.xlanguage = ''
        self.xscreenshots = '//dl[@id="previewItem"]/dt[@class="thumb"]/a'

    def getAppId(self):
        match = re.match(r'.*ovi.com/content/([0-9]+)[^0-9]*', self.url)
        if match:
            return match.groups(0)[0]

    def getResource1(self, app_id):
        return 'http://store.ovi.com/content/'+app_id

    def getCost(self):
        price = self._do_xpath(self.xcost)
        if price:
            price = price.replace('Gratis','')
            price = re.sub(r'[^0-9,\.]','', price)
        return cast_as_float(price) if price else 0.0

    def getUpdated(self):
        return datetime.now().strftime('%Y-%m-%d')

    def getScreenshots(self):
        screenshots = []
        elem = self.tree.xpath(self.xscreenshots) if self.xscreenshots else []
        if len(elem):
            screenshots = [a.attrib.get('href') for a in elem]
        return screenshots

class AppInfoGrabber(object):

    def __init__(self, url, html=None):
        self.url = url
        self.html = html
        self.extractor = None
        self.market = self._detectMarket()
        self.fallback_langs = "Deutsch, Englisch"


    def _detectMarket(self):
        if re.match(r'^http[s]?:\/\/market\.android\.', self.url) or \
                re.match(r'^http[s]?:\/\/play\.google\.', self.url) :
            self.extractor = AndroidExtractor
            return 'android'
        elif re.match(r'^http[s]?:\/\/(www\.)?windowsphone\.com', self.url):
            self.extractor = WindowsExtractor
            return 'windows'
        elif re.match(r'^http[s]?:\/\/itunes\.apple\.com', self.url):
            self.extractor = IphoneExtractor
            return 'iphone'
        elif re.match(r'^http[s]?:\/\/store\.ovi\.com', self.url):
            self.extractor = NokiaExtractor
            return 'nokia'
        else:
            raise NoAppLinkException('No known app link')

    def _getHtml(self, url):
		try:
			res = browser.get(url)
			html = res.content
		except:		
			html = ''
		return html
    
    def _loadHtml(self) :
		if not self.html:
			self.html = self._getHtml(self.url)
		return self.html

    def _load(self):
		self._loadHtml()
		parser =  etree.HTMLParser(encoding="utf-8")
		return etree.parse(StringIO(self.html), parser)

    def extract(self):
        htmlTree = self._load()
        extractor = self.extractor(htmlTree, self.url)
        extractor.getTreeScraper(self.html)
        app_id = extractor.getAppId()
        result = {
            'url': self.url,
            'market': self.market,
            'app_id': app_id,
            'title': extractor.getTitle(),
            'marketdesc': extractor.getMarketDesc(),
            'shortdesc': '',
            'longdesc': extractor.getDescription(),
            'resource1': extractor.getResource1(app_id),
            'resource2': extractor.getResource2(app_id),
            'icon1':  extractor.getIcon(),
            'publisher': extractor.getPublisher(),
            'cost': extractor.getCost(),
            'release_update': extractor.getUpdated(),
            'category_market': extractor.getCategory(),
            'version': extractor.getVersion(),
            'requirement': extractor.getRequired(),
            'rating': extractor.getRating(),
           'language': extractor.getLanguage(),
            'screenshots': extractor.getScreenshots(),
            'purchases' : extractor.getPurchases(),
            'ratings' : extractor.getRatings(),
        }
        if not result['language']:
            result['language'] = self.fallback_langs
        result['language_hidden'] = result['language']

        return result


if __name__ == '__main__' :
	a="https://itunes.apple.com/mx/app/reforma/id322385772?mt=8"
	i=AppInfoGrabber(a)
	import pprint
	pprint.pprint(i.extract())

