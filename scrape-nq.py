from scraper.scrapelib import TreeScraper, TextEditor,TextParser
import os, sys
import logging
from collections import defaultdict
import pprint
debug=True



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
		           "./preceding-sibling::p[3]//i//text()",
		           
		           ) :
			tff=table.extract(fund=tg)
			if "fund" in tff :
				logger.debug("%s fund: %s" % (tg,repr(tff["fund"])))
				tm["fund"]=sharename(strippct("".join(tff["fund"])))
				break
		if "fund" in tm :
			tm["fund"]=sharename(strippct("".join(tm["fund"])))
		for row in table.select("tr"):
			rcat=row.extract(category="td[1]//b//text()")
			if "category" in rcat :
				rcat["category"]=strippct(sharename(rcat["category"]))
				tm.update(rcat)
			else :
				r=row.extract(share="td[1]//text()[2]",
						  left="td[1]//p[contains(@style,'margin-left:1.00em;')]//text()",
						  indented="td[1]//p[contains(@style,'margin-left:3.00em;')]//text()",
						  price="td[8]//text()",
						  price2="td[7]//text()",
						  number="td[4]//text()")
				#logger.debug(repr(r))
				if "left" in r :
					tm["left"]="".join(r["left"])
				r.update(tm)
				if ("price" in r) and ("number" in r) and ("share" in r) : # and ("".join(r["category"]).find("GERMANY")>-1):
					try :
						for lt in ("price","number","price2") :
							if type(r[lt])==type([]):
								r[lt]="".join(r[lt])
						r["price"]=sharename(r["price"].replace(",",""))
						r["price2"]=sharename(r["price2"].replace(",",""))
						if r["price"]=="" :
							r["price"]=r["price2"]

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

