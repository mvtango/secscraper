from lxml import etree
import simplejson
import pprint
import re
import string
import os
from unicodecsv import UnicodeWriter
from scraper.scrapelib import TextParser
# from processor import GenericProcessor
# process=GenericProcessor()

fnmeta=TextParser([r"data/html/(?P<date>\d\d\d\d-\d\d-\d\d)T\d\d:\d\d:\d\d-\d\d:\d\d-(?P<fund>\d+)"])

ff="""
data/html/2012-06-29T12:22:02-04:00-0001100663-d370583dnq.htm
data/html/2012-07-26T11:07:46-04:00-0001165216-i00306_bhd-nq.htm
data/html/2012-07-27T14:11:15-04:00-0000830474-i00324_his-nq.htm
data/html/2012-07-27T14:11:54-04:00-0001222401-i00325_hyt-nq.htm
data/html/2012-07-27T14:12:40-04:00-0001160469-i00326_hyv-nq.htm
data/html/2012-07-30T12:17:04-04:00-0001100663-d381299dnq.htm
data/html/2012-07-30T12:18:37-04:00-0000930667-d381444dnq.htm
data/html/2012-08-27T16:02:09-04:00-0001398078-d383021dnq.htm
data/html/2012-08-29T13:55:12-04:00-0001100663-d401274dnq.htm
data/html/2012-09-25T15:50:02-04:00-0001062805-d414908dnq.htm
data/html/2012-09-25T15:50:05-04:00-0001062806-d414908dnq.htm
data/html/2012-09-25T16:09:06-04:00-0001320375-d412678dnq.htm
data/html/2012-09-25T16:10:01-04:00-0001393299-d412686dnq.htm
data/html/2012-09-25T16:10:58-04:00-0001280936-d412694dnq.htm
data/html/2012-09-25T16:11:09-04:00-0001398078-d412705dnq.htm
data/html/2012-09-26T09:44:00-04:00-0001324285-i00398_gde-nq.htm
data/html/2012-09-26T09:53:24-04:00-0000834237-e50017_nq.htm
data/html/2012-09-28T12:09:15-04:00-0001100663-d410831dnq.htm
data/html/2012-09-28T12:15:06-04:00-0001100663-d410756dnq.htm
data/html/2012-09-28T12:17:11-04:00-0000930667-d410837dnq.htm
data/html/2012-11-21T13:59:14-05:00-0000893818-d439161dnq.htm
data/html/2012-11-21T16:04:14-05:00-0001398078-d439150dnq.htm
data/html/2012-11-26T12:52:37-05:00-0000835620-i00450_wif-nq.htm
data/html/2012-11-26T14:08:40-05:00-0000355916-d442662dnq.htm
data/html/2012-11-26T15:09:57-05:00-0000790525-d442212dnq.htm
data/html/2012-11-27T10:24:30-05:00-0000319108-e50814nq.htm
data/html/2012-11-27T11:59:59-05:00-0000922457-d442216dnq.htm
data/html/2012-11-28T10:17:26-05:00-0001026144-i00449_if-nq.htm
data/html/2012-12-28T13:22:34-05:00-0001100663-d450388dnq.htm
data/html/2013-01-29T13:51:49-05:00-0000930667-d468261dnq.htm
data/html/2013-01-29T13:53:05-05:00-0001100663-d468173dnq.htm
data/html/2013-02-27T10:32:14-05:00-0001398078-d487579dnq.htm
data/html/2013-03-01T13:04:07-05:00-0001100663-d488313dnq.htm
data/html/2013-03-26T14:32:05-04:00-0001062806-d499607dnq.htm
data/html/2013-03-26T14:37:07-04:00-0001320375-d499542dnq.htm
data/html/2013-03-26T14:39:07-04:00-0001393299-d499614dnq.htm
data/html/2013-03-26T14:48:13-04:00-0001062805-d499607dnq.htm
data/html/2013-03-26T14:52:01-04:00-0001398078-d499637dnq.htm
data/html/2013-03-26T14:52:04-04:00-0001280936-d499622dnq.htm
data/html/2013-03-26T15:45:49-04:00-0000834237-e52578nq.htm
data/html/2013-03-28T12:51:18-04:00-0001100663-d503998dnq.htm
data/html/2013-03-28T12:56:12-04:00-0001100663-d505226dnq.htm
data/html/2013-03-28T12:59:05-04:00-0000930667-d503949dnq.htm
data/html/2013-05-24T10:49:54-04:00-0000835620-d537851dnq.htm
data/html/2013-05-24T11:19:59-04:00-0000790525-d536279dnq.htm
data/html/2013-05-24T13:44:03-04:00-0001026144-d538216dnq.htm
data/html/2013-05-24T14:40:02-04:00-0000922457-d536283dnq.htm
data/html/2013-05-24T15:51:09-04:00-0000893818-d537937dnq.htm
data/html/2013-05-24T16:33:07-04:00-0001398078-d541053dnq.htm
data/html/2013-05-24T16:38:14-04:00-0000355916-d540855dnq.htm
data/html/2013-05-28T09:07:46-04:00-0000319108-d540823dnq.htm
data/html/2013-06-27T15:18:35-04:00-0001100663-d555685dnq.htm
"""

files={ "in" : ff.split("\n"),
        "csv" : "data/germany.csv" }


parse={
       "container" : "//table",
       "properties" : {
			"date" : "//p/font[contains(text(),'Date of reporting period')]/text()",
			"fund" : [ "//table[1]/tr/td//p/font[contains(text(),'Name of Fund')]/../../../../tr[1]/td[2]/p/font/text()",
					   "//p/font[contains(text(),'Name of Fund:')]/text()" ]
       },
       "row" : ".//tr",
       "columns" : {
				"category" : "./td[1]//font[@size='2']/b/text()",
				"name" : "./td[1]//font[@size='2']/text()",
				"shares" : "./td[4]//font[@size='2']/text()",
				"value" : ["./td[7]//font[@size='2']/text()", "./td[8]//font[@size='2']/text()"] ,

      },
      "ok" : [
				"name|shares|value",

      ],
      "table" : [ "file","fund","date","category","name","shares","value"]
      
}


unifier= [
	{ 're' : re.compile("^[0-9,]+$"), 'repl' : lambda a: a.string.replace(",","") },
	{ 're' : re.compile("\s\s+"), 'repl' : " " },
	{ 're' : re.compile("^\s"), 'repl' : "" },
	{ 're' : re.compile("\s$"), 'repl' : "" },
	{ 're' : re.compile("Date of reporting period: (\d\d)/(\d\d)/(\d\d\d\d)"), 'repl' : r"\3-\2-\1" },
	{ 're' : re.compile("\s+\(concluded\)"), 'repl' : "" },
	{ 're' : re.compile("\s+\(continued\)"), 'repl' : "" },
	{ 're' : re.compile("\s*\x97.*",re.DOTALL), 'repl' : "" },
	{ 're' : re.compile("\s*\x96.*",re.DOTALL), 'repl' : "" },
	{ 're' : re.compile(", Inc.:?"), 'repl' : "" },
	{ 're' : re.compile("^\xa0"), 'repl' : "" },
	{ 're' : re.compile("^\$"), 'repl' : "" },

]


def extract(e,p) :
	if type(p)==type("") :
		p=[p]
	for pp in p :
		try :
			a=e.xpath(pp)
			if a: 
				return a
		except Exception, e:
			print "pp %s - unmatched" % pp
			pass
	return None

def stringstring(a) :
	try :
		s=etree.tostring(a)
	except TypeError :
		if type(a) == type([]) :
			s="".join(a)
		else :
			s=a
	for u in unifier :
		try :
			s=u['re'].sub(u["repl"],s)
		except Exception, e:
			pass
	return s



def output_ok(h,fields) :
	fs=fields.split("|")
	return set(fs)==set(filter(lambda a: h[a],h.keys()))
	
	
def output_row(h,row) :
	rrow=[]
	for f in row :
		if f in h:
			rrow.append(h[f])
		else :
			rrow.append("")
	return rrow



ofile=UnicodeWriter(open(files["csv"],"w"))
for fn in files["in"] :
	try :
		tree=etree.parse(open(fn),etree.HTMLParser())

		data=[]
		drows=0
		props=fnmeta(fn)
		props["file"]=os.path.split(fn)[1]
		for (k,v) in parse["properties"].items() :
			a=stringstring(extract(tree,v))
			if a is not None:
				props[k]=a
		#pprint.pprint(props)
		for container in tree.xpath(parse["container"]) :
			cdata=[]
			for row in container.xpath(parse["row"]) :
				rd={}
				# print "row: %s" % (etree.tostring(row)[:10])
				for (k,x) in parse["columns"].items() :
					if type(x) != type([]) :
						x=[x]
					a=[]
					for xx in x :
						a.extend(row.xpath(xx))
					if a:
						# print "matched"
						rd[k]="".join([stringstring(ss) for ss in a])
						if len(rd[k]) == 1 :
							rd[k]=rd[k][0]
				of=False
				props.update(rd)
		
				for o in parse["ok"] :
					if output_ok(rd,o) :
						cdata.append(output_row(props,parse["table"]))
						of=True
						break
		#		if not of:
		#			rd.update({"file" : "o"})
		#			cdata.append(output_row(rd,parse["table"]))
				
			drows=drows+len(cdata)
			data.append(cdata)
	except Exception,e:
		print "%s - error %s" % (fn,e) 
	else :
		print "%s - success - %s tables, %s records" % (fn,len(data),drows)

		# pprint.pprint(map(lambda a:  { "a" : a.get("reaction","-"), "b" : a.get("color",""), "c" : a.get("amendment","") },data));
		for container in data :
			if len(container)>0 :
				ofile.writerows(container)
			
