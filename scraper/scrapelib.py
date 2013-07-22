from lxml import etree 
from lxml.cssselect import CSSSelector, SelectorSyntaxError
from lxml import etree





import requests
import re

class AddToChain :
    
	def __add__(self,o) :
        	def a(*args,**kwargs) :
            		return self(o(*args,**kwargs))
        	return a



class TextEditor(AddToChain):
	"""
	Takes List of Search / Replace Expressions
	d=TextEditor([("a","b"),("c","d")])

	d.process("maca") -> "mbdb"
	"""
	
	def __init__(self, ruleset) :
		self.ruleset=[(re.compile(a[0]),a[1]) for a in ruleset]


	def edit(self,i) :
		for r in self.ruleset :
			i=r[0].sub(r[1],i)
		return i 

	def __call__(self,i) :
		return self.edit(i)




class TextParser(AddToChain) :
	"""
	Takes List of Regexp. Will return groupdict() of first match
	
	"""


	def __init__(self, ruleset) :
		self.ruleset=[re.compile(a) for a in ruleset]


	def parse(self,i) :
		for r in self.ruleset :
			m=r.search(i)
			if m :
				return m.groupdict()
		return None 


	def __call__(self,i) :
		return self.parse(i)



class ScrapedElement(etree.ElementBase) :
	
	def extract(self,a=None) : 
		t=etree.tostring(self)
		if type(a) == type("") :
			a=TextParser([a])	
		if a :
			t=a(t)
		return t
		
	def select(self,p) :
		try :
			sel=CSSSelector(p)
			return sel(self)
		except SelectorSyntaxError :
			return self.xpath(p) 
		
	
	def extract(self, **args) :
		r={}
		for (k,v) in args.items() :
			vv=self.select(v)
			if vv :
				r[k]=vv
		return r
	
	def __repr__(self) :
		return self.extract()


def myparser() :
	parser_lookup = etree.ElementDefaultClassLookup(element=ScrapedElement)
	parser = etree.HTMLParser()
	parser.set_element_class_lookup(parser_lookup)
	return parser






class TreeScraper :
	

	def __init__(self, ss) :
		if ss[0]=="<" :
			self.tree=etree.fromstring(ss,myparser())
		else :
			self.tree=etree.parse(ss,myparser())


	def select(self,p) :
		try :
			sel=CSSSelector(p)
			return sel(self.tree)
		except SelectorSyntaxError :
			return self.tree.xpath(p) 


	def extract(self,xp,processor=None) :
		r=self.select(xp)
		if type(r) == type("") :
			r=[r]
		if processor :
			res=[ processor(etree.tostring(a)) for a in r ]	
		else :
			res=[ etree.tostring(a) for a in r ]	
		return res
		

		





if __name__=="__main__" :

	chinese=TextEditor([("r","l"),("a","m")])
	assert chinese.edit("roaring")=="lomling"

	firstlast=TextParser([r"(?P<first>\d+)(?P<last>.+)",r"(?P<last>\D+)(?P<first>\d+)"])
	assert firstlast.parse("3a")=={ "first":"3", "last" : "a"}
	assert firstlast("a3")=={ "first":"3", "last" : "a"}

	t=TreeScraper("<html><h1>Headline</h1><p>Hallo Welt</p></html>")

	assert t.select("//h1/text()")==['Headline']
	assert t.extract("h1")==['<h1>Headline</h1>']

	notags=TextEditor([["<[^>]+>",""]])

	print t.extract("h1",notags)
	print t.extract("h1",chinese)
	print t.extract("h1",chinese+notags)
	


