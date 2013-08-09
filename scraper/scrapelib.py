# coding: utf-8

from lxml import etree 
from lxml.cssselect import CSSSelector, SelectorSyntaxError
import types
import requests
import re
import logging
import os

logger=logging.getLogger(os.path.split(__file__)[1])


class AddToEditorChainClass :
	
	
	def __init__(self) :
		self._debug=False

    
	def __add__(self,o) :
        	def a(*args,**kwargs) :
            		return self(o(*args,**kwargs))
        	return a


	def makestring(self,a) :
		if type(a)==types.ListType :
			a="".join([unicode(b) for b in a])
		return a
		
		
	def debug(self,state=None) :
		if state is not None :
			self._debug=state
		return self._debug


class TextEditor(AddToEditorChainClass):
	"""
	Takes List of Search / Replace Expressions
	d=TextEditor([("a","b"),("c","d")])

	d.process("maca") -> "mbdb"
	"""
	
	def __init__(self, ruleset) :
		AddToEditorChainClass.__init__(self)
		self.ruleset=[(re.compile(a[0]),a[1]) for a in ruleset]


	def edit(self,i) :
		i=self.makestring(i)
		if self.debug() :
			logger.debug("Start: %s" % repr(i))
		for r in self.ruleset :
			i=r[0].sub(r[1],i)
			if self.debug() :
				logger.debug("%s->%s : %s" % (r[0].pattern,r[1],repr(i))) 
			
		return i 

	def __call__(self,i) :
		return self.edit(i)




class TextParser(AddToEditorChainClass) :
	"""
	Takes List of Regexp. Will return groupdict() of first match
	
	"""


	def __init__(self, *ruleset) :
		AddToEditorChainClass.__init__(self)
		self.ruleset=[re.compile(a) for a in ruleset]


	def parse(self,i) :
		i=self.makestring(i)
		for r in self.ruleset :
			m=r.search(i)
			if m :
				return m.groupdict()
		return None 


	def __call__(self,i) :
		return self.parse(i)



class ScrapedElement(etree.ElementBase) :
	
	def text(self,parse=None) : 
		t=etree.tostring(self)
		if type(parse) in types.StringTypes :
			parse=TextParser(parse)		
		if type(parse) == types.FunctionType :
			t=parse(t)
		return t
		
	def select(self,p) :
		try :
			sel=CSSSelector(p)
			return sel(self)
		except SelectorSyntaxError :
			return self.xpath(p) 
		except AssertionError :
			return self.xpath(p) 
		
	
	def extract(self, **args) :
		r={}
		for (k,v) in args.items() :
			vv=self.select(v)
			if vv :
				if len(vv)==1 :
					r[k]=vv[0]
				else :
					r[k]=vv
		return r
	
	def __repr__(self) :
		return self.text()


def myparser() :
	parser_lookup = etree.ElementDefaultClassLookup(element=ScrapedElement)
	parser = etree.HTMLParser()
	parser.set_element_class_lookup(parser_lookup)
	return parser


class TreeScraper :
	
	def __init__(self, ss) :
		if type(ss) in types.StringTypes and len(ss)>0 and ss[0]=="<" :
			self.tree=etree.fromstring(ss,myparser())
		else :
			self.tree=etree.parse(ss,myparser())


	def select(self,p) :
		try :
			sel=CSSSelector(p)
			return sel(self.tree)
		except SelectorSyntaxError :
			return self.tree.xpath(p) 
		except AssertionError :
			return self.tree.xpath(p) 

	def extract(self,*args,**kwargs) :
		""" with select expression as first arg: returns array of match dicts, without: returns match dicts"""
		r=[]
		if len(args) == 1 :
			for e in self.select(args[0]) :
				if hasattr(e,"extract") :
					e=e.extract(**kwargs)
				r.append(e)
			return r
		else :
			if len(args)==0 :
				r=self.tree.getroot()
				if hasattr(r,"extract") :
					return r.extract(**kwargs)
				else :
					return {} 
			else :
				raise(TypeError,"extract() takes 0 or 1 arguments + keyword arguments, got %s" % len(args))
				
			
		





if __name__=="__main__" :

	chinese=TextEditor([("r","l"),("a","m")])
	assert chinese.edit("roaring")=="lomling"

	firstlast=TextParser(r"(?P<first>\d+)(?P<last>.+)",r"(?P<last>\D+)(?P<first>\d+)")
	assert firstlast.parse("3a")=={ "first":"3", "last" : "a"}
	assert firstlast("a3")=={ "first":"3", "last" : "a"}

	t=TreeScraper("<html><h1>Headline</h1><p>Hallo <b>Welt</b>, Du bist so <b>sch&ouml;n</b></p><p>Nat&uuml;rlich <b>nicht immer</b></html>")

	assert t.select("//h1/text()")==['Headline']
	print "e=", t.extract("p",text='b')
	notags=TextEditor([["<[^>]+>",""]])

	print notags(u"blöd")
	#print t.extract("h1",notags)
	#print t.extract("h1",chinese)
	#print t.extract("h1",chinese+notags)
	


