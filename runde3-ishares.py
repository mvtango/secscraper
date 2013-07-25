from scraper.scrapelib import TreeScraper, TextEditor,TextParser
import os, sys
import logging
from collections import defaultdict

debug=True



if debug :
	logging.basicConfig(file=sys.stderr,level=logging.DEBUG)


(_here,_me)=os.path.split(__file__)
_me=os.path.splitext(_me)[0]


output_dir="%s/output" % _here

input_files="""data/html/2013-03-01T13:04:07-05:00-0001100663-d488313dnq.htm
data/html/2013-03-28T12:51:18-04:00-0001100663-d503998dnq.htm
data/html/2013-03-28T12:56:12-04:00-0001100663-d505226dnq.htm
data/html/2013-03-28T12:59:05-04:00-0000930667-d503949dnq.htm
data/html/2013-03-26T14:52:01-04:00-0001398078-d499637dnq.htm
data/html/2013-03-28T12:42:09-04:00-0000930667-d504385dnq.htm"""




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


def parsefile(fn) :
	t=TreeScraper(fn)
	res=[]
	tm={"file" : fn,  "date" : datex(fn)}
	for table in t.select("//table"):
		tm.update(table.extract(fund="../preceding-sibling::p[3]//i//text()"))
		if "fund" in tm :
			tm["fund"]=strippct("".join(tm["fund"]))
		for row in table.select("tr"):
			rcat=row.extract(category="td//b//text()")
			if "category" in rcat :
				rcat["category"]=strippct(sharename(rcat["category"]))
				tm.update(rcat)
			else :
				r=row.extract(share="td[1]//text()[2]",
						  price="td[8]//text()",
						  number="td[4]//text()")
				r.update(tm)
				if ("price" in r) and ("number" in r) and ("share" in r) : # and ("".join(r["category"]).find("GERMANY")>-1):
					r["price"]=sharename(r["price"][0].replace(",",""))
					r["number"]=sharename(r["number"][0].replace(",",""))
					r["share"]=sharename(r["share"][0])
					res.append(r)
        return res

rr=[]
for f in input_files.split("\n")[:5] :
    try :
        n=parsefile(f)
        if n : 
			print "%s - %s" % (len(n),f)
			rr.extend(n)
        else :
            print "!! - %s" % (f,)
    except Exception, e:
		raise
		print "!!! - %s - %s" % (f,e)
        
import simplejson,string

rr_germany=filter(lambda a : string.lower("%(category)s %(share)s %(fund)s" % defaultdict(lambda:"",a)).find("germany")>-1,rr)
simplejson.dump(rr,open(os.path.join(output_dir,"resultate-%s.json" % _me ),"w"))
simplejson.dump(rr_germany,open(os.path.join(output_dir,"resultate-%s-germany.json" % _me),"w"))

from unicodecsv import UnicodeWriter

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr))

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s-germany.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr_germany))

