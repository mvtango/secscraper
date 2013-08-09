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


output_dir="%s/output" % _here

input_files="""data/2013-03-26T14:32:05-04:00-0001062806-d499607dnq.htm
data/2013-03-26T14:37:07-04:00-0001320375-d499542dnq.htm
data/2013-03-26T14:39:07-04:00-0001393299-d499614dnq.htm
data/2013-03-26T14:52:01-04:00-0001398078-d499637dnq.htm
data/2013-03-26T14:52:04-04:00-0001280936-d499622dnq.htm
data/2013-05-24T10:49:54-04:00-0000835620-d537851dnq.htm
data/2013-05-24T11:19:59-04:00-0000790525-d536279dnq.htm
data/2013-05-24T13:44:03-04:00-0001026144-d538216dnq.htm
data/2013-05-24T14:40:02-04:00-0000922457-d536283dnq.htm
data/2013-05-24T15:51:09-04:00-0000893818-d537937dnq.htm
data/2013-05-24T16:33:07-04:00-0001398078-d541053dnq.htm
data/2013-05-24T16:38:14-04:00-0000355916-d540855dnq.htm
data/2013-05-28T09:07:46-04:00-0000319108-d540823dnq.htm"""


# keine positionen: data/2013-03-26T14:48:13-04:00-0001062805-d499607dnq.htm
# data/2013-03-28T12:42:09-04:00-0000930667-d504385dnq.htm



# nicht erkannt: data/2013-03-26T15:45:49-04:00-0000834237-e52578nq.htm



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
		tm.update(table.extract(fund="../preceding-sibling::p[3]//i//text()"))
		if "fund" in tm :
			tm["fund"]=sharename(strippct("".join(tm["fund"])))
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
					try :
						r["price"]=sharename(r["price"].replace(",",""))
						r["number"]=sharename(r["number"].replace(",",""))
						r["share"]=sharename(r["share"])
						res.append(r)
					except Exception,e :
						logger.debug("%s -%s" % (e,pprint.pformat(r)))
        return res

rr=[]
for fs in input_files.split("\n"):
    f=os.path.join("/home/martin/Dropbox/blackrock-scraper/",fs)
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
        
import simplejson,string

rr_germany=filter(lambda a : string.lower("%(category)s %(share)s %(fund)s" % defaultdict(lambda:"",a)).find("germany")>-1,rr)
simplejson.dump(rr,open(os.path.join(output_dir,"resultate-%s.json" % _me ),"w"))
simplejson.dump(rr_germany,open(os.path.join(output_dir,"resultate-%s-germany.json" % _me),"w"))

from unicodecsv import UnicodeWriter

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr))

uw=UnicodeWriter(open(os.path.join(output_dir,"resultate-%s-germany.csv" % _me),"w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a.get("fund",""),a["share"],a["number"],a["price"],a["file"]], rr_germany))

