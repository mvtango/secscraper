from scraper.scrapelib import TreeScraper, TextEditor,TextParser
import os, sys
import logging
from collections import defaultdict
import pprint
debug=True
import re



if debug :
	logging.basicConfig(file=sys.stderr,level=logging.DEBUG)

logger=logging.getLogger(os.path.split(__file__)[1])

(_here,_me)=os.path.split(__file__)
_me=os.path.splitext(_me)[0]


output_dir="%s/data/vereinigungsmenge/output" % _here

input_files=sys.argv[1:]



datex=TextEditor([[r"^.*/(\d{4}-\d{2}-\d{2}).*$",r"\1"]])

sharename=TextEditor([[r"[\s\r\n]+"," "],
					  [r" *\(concluded\) *", "" ],
					  [r" *\(continued\) *", "" ],
					  [r"\xa0", " " ],
				      [r"\s\s+"," " ],
				      [r"^\s+"  ,  ""],
					  [r"\s+$"  ,  ""],
					  [r"\s*\x97.*", "" ],
					  [r"\s*\x96.*","" ],
					  ])

sharename.debug(False)

					  
strippct=TextEditor([[r" [0-9\.]+%$",""]])
# strippct.debug(True)

stripname=TextEditor([[r"Name of Fund:",""]])

def parsefile(fn) :
	t=TreeScraper(fn)
	res=[]
	tm={"file" : os.path.split(fn)[1],  "date" : datex(fn)}
	nof=t.extract(fund="//*[contains(text(),'Name of Fund:')]/text()")
	if "fund" in nof :
		nof["fund"]=stripname(nof["fund"])
		tm.update(nof)
	for table in t.select("//table"):
		for tg in ("../preceding-sibling::p[3]//i//text()",
		           "../preceding-sibling::table//tr[3]//td[2]//b//text()[1]",
		           "./preceding-sibling::table[1]/tr[2]/td[3]//b/text()[1]",
		           "./preceding-sibling::table[1]/tr[3]/td[3]//b/text()[1]",
		           "../preceding-sibling::div[1]//table[1]/tr[2]/td[contains(@style,'text-align: right')]//text()[1]",
		           "./preceding-sibling::p[3]//i//text()",
		           
		           ) :
			tff=table.extract(fund=tg)
			if "fund" in tff :
				logger.debug("%s fund: %s" % (tg,repr(tff["fund"])))
				tm["fund"]=sharename(strippct("".join(tff["fund"])))
				break
		if "fund" in tm :
			tm["fund"]=sharename(strippct("".join(tm["fund"])))
		tm["category"]=""
		tm["akku"]=[]
		for row in table.select("tr"):
			rcat=row.extract(category=".//td[contains(@colspan,'9')]//text()")
			if "category" in rcat :
				logger.debug("Category: %s" % repr(rcat))
				rcat["category"]=strippct(sharename(rcat["category"]))
				tm.update(rcat)
			else :
				r=row.extract(share="td[1]//text()",
						  left="td[1][starts-with(@style,'text-align: left')]/text()",
						  indent="td[1][contains(@style,'text-indent:')]/text()",
						  number="td[2]//text() | td[3]//text() | td[4]//text() | td[5]//text() | td[6]//text() | td[7]//text() | td[8]//text()",
						  )
				if ("share" in r) and (not "left" in r) and (not "indent" in r) :
					tm["category"]=strippct(sharename(r["share"]))
				if "number" in r :
					r["number"]=filter(lambda a: re.match(r"\s*\(?\d",a),r["number"])
					if len(r["number"])==2 :
						r["price"]=r["number"][1]
						r["number"]=r["number"][0]
				if "number" in r :
					if r["number"]==[] :
						if "indent" in r :
							tm["akku"].append("".join(r["share"]))
						else :
							if "share" in r :
								tm["akku"]=["".join(r["share"]),]
					else :
						if tm["akku"] :
							if "indent" in r :
								r["share"]="%s %s" % (" ".join(tm["akku"]),r["share"])
							ta=tm["akku"][0]
							tm["akku"]=[]
							tm["akku"].append(ta)
				logger.debug(repr(r))
				r.update(tm)
				if ("price" in r) and ("number" in r) and ("share" in r) : # and ("".join(r["category"]).find("GERMANY")>-1):
					try :
						for lt in ("price","number") :
							if type(r[lt])==type([]):
								r[lt]="".join(r[lt])
						r["price"]=sharename(r["price"].replace(",",""))
				
						r["number"]=sharename(r["number"].replace(",",""))
						if "indented" in r :
							r["share"]=sharename(tm["left"]+" "+r["share"])
						else :
							r["share"]=sharename(r["share"])
						if (r["price"]>"") and (r["number"]>""):
							res.append(r)
					except Exception,e :
						logger.debug("%s -%s" % (e,pprint.pformat(r)))
        return res

rr=[]
for f in input_files:
	try :
		n=parsefile(f)
		if n : 
			print "%s - %s" % (len(n),f)
			rr.extend(n)
		else : 
			print "!! - %s " % (f,)
	except Exception, e:
		raise
		print "!!! - %s - %s" % (f,e)
	_me=os.path.splitext(os.path.split(f)[1])[0]

import simplejson,string

rr_germany=filter(lambda a : string.lower("%(category)s %(share)s %(fund)s" % defaultdict(lambda:"",a)).find("germany")>-1,rr)
simplejson.dump(rr,open(os.path.join(output_dir,"resultate-%s.json" % _me ),"w"))
simplejson.dump(rr_germany,open(os.path.join(output_dir,"resultate-%s-germany.json" % _me),"w"))

from unicodecsv import UnicodeWriter

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr))

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s-germany.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr_germany))

