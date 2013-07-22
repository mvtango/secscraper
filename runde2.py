from scraper.scrapelib import TreeScraper, TextEditor,TextParser
ffn="""data/html/2012-07-27T14:12:40-04:00-0001160469-i00326_hyv-nq.htm
data/html/2012-08-27T16:02:09-04:00-0001398078-d383021dnq.htm
data/html/2012-09-25T15:50:02-04:00-0001062805-d414908dnq.htm
data/html/2012-09-25T15:50:05-04:00-0001062806-d414908dnq.htm
data/html/2012-09-25T16:09:06-04:00-0001320375-d412678dnq.htm
data/html/2012-09-25T16:10:01-04:00-0001393299-d412686dnq.htm
data/html/2012-09-25T16:10:58-04:00-0001280936-d412694dnq.htm
data/html/2012-09-25T16:11:09-04:00-0001398078-d412705dnq.htm
data/html/2012-09-26T09:53:24-04:00-0000834237-e50017_nq.htm
data/html/2012-11-21T16:04:14-05:00-0001398078-d439150dnq.htm
data/html/2012-11-27T10:24:30-05:00-0000319108-e50814nq.htm
data/html/2012-11-27T11:59:59-05:00-0000922457-d442216dnq.htm
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
data/html/2013-05-24T16:33:07-04:00-0001398078-d541053dnq.htm
data/html/2013-05-24T16:38:14-04:00-0000355916-d540855dnq.htm
data/html/2013-05-28T09:07:46-04:00-0000319108-d540823dnq.htm
data/html/2013-06-27T15:18:35-04:00-0001100663-d555685dnq.htm"""




datex=TextEditor([[r"^.*/(\d{4}-\d{2}-\d{2}).*$",r"\1"]])

sharename=TextEditor([[r"[\r\n]+"," "],
				      ["\s\s+"," " ],
				      ["^\s"  ,  ""],
					  ["\s$"  ,  ""],
					  ["\s*\x97.*", "" ],
					  ["\s*\x96.*","" ],
					  ["^\xa0", "" ],
					  [" *\(concluded\) *", "" ],
					  ])
					  


def parsefile(fn) :
	t=TreeScraper(fn)
	res=[]
	tm={"file" : fn,  "date" : datex(fn)}
	for table in t.select("//table"):
		tm.update(table.extract(fund="../preceding-sibling::p[3]//i//text()"))
		if "fund" in tm :
			tm["fund"]=sharename("".join(tm["fund"]))
		for row in table.select("tr"):
			rcat=row.extract(category="td//b//text()")
			if "category" in rcat :
				rcat["category"]=sharename("".join(rcat["category"]))
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
for f in ffn.split("\n") :
    try :
        n=parsefile(f)
        if len(n)>0 :
            rr.extend(n)
            print "%s - %s" % (len(n),f)
        else :
            print "!! - %s" % (f,)
    except Exception, e:
		raise
		print "!!! - %s - %s" % (f,e)
        
import simplejson,string

rr_germany=filter(lambda a : string.lower("%(category)s %(share)s" % a).find("germany")>-1,rr)
simplejson.dump(rr,open("data/resultate-runde2.json","w"))
simplejson.dump(rr_germany,open("resultate-runde2-germany.json","w"))

from unicodecsv import UnicodeWriter

uw=UnicodeWriter(open("data/resultate-runde2.csv","w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a["share"],a["number"],a["price"],a["file"]], rr))

uw=UnicodeWriter(open("data/resultate-runde2-germany.csv","w"),delimiter=";")
uw.writerows(map(lambda a: [a["date"],a["category"],a["share"],a["number"],a["price"],a["file"]], rr_germany))

