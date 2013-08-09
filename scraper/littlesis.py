# coding: utf-8

from scraper.browser import Browser
from lxml import etree

class LittleSisBrowser(Browser) :
	
	_key="223643a835ec11609db34615df8687076f981056"
	
	def __init__(self, *args,**kwargs) :
		super(LittleSisBrowser,self).__init__(*args,**kwargs)
		self.headers.update({ 'Accept-Encoding' : "gzip" })
	
	
	def get(self,addr,*args,**kwargs) :
		j="?"
		if addr.find("?") > 0 :
			j="&"
		addr="%s%s_key=%s" % (addr,j,LittleSisBrowser._key)
		return super(LittleSisBrowser,self).get(addr,*args,**kwargs)
		
		
	def tree(self,*args,**kwargs) :
		c=self.get(*args,**kwargs)
		return etree.fromstring(c.content, etree.XMLParser(remove_blank_text=True))


def writeXML(tree,fname) :
	f=open(fname,"w")
	f.write(etree.tostring(tree,pretty_print=True))
	f.close()
		

relationship={ 'Position' : '1',
             'Education' : '2',
             'Membership' : '3',
			 'Family' : '4',
			 'Donation' : '5',
			 'Transaction' : '6',
			 'Lobbying' : '8',
			 'Social' : '9',
			 'Professional' : '10'
}
