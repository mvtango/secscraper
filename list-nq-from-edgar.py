import logging,sys,os
from lxml import etree 
import requests
from dumptruck import DumpTruck, Pickle

_here=os.path.split(__file__)[0]

store=DumpTruck(dbname=os.path.join(_here,"db/documents.db"))

parser=etree.HTMLParser()

def getTree(url) :
	return etree.parse(url,etree.HTMLParser())

logger=logging.getLogger(os.path.split(__file__)[1])
logging.basicConfig(level=logging.DEBUG, file=sys.stderr)

def get_nq_for_cik(cik) :
	try :
		tree=getTree("http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=N-Q%%25&dateb=&owner=include&start=0&count=40&output=atom" % cik)
	except Exception, e :
		logger.error("Error searching for CIK %s:%s" % (cik,e))
		pass
	for entry in tree.xpath("//entry") :
		link=entry.xpath("link/@href")[0]
		date=entry.xpath("updated/text()")[0]
		r={"date" : date, "link" : link }
		stree=getTree(link)
		r["doc"]="http://www.sec.gov%s" % stree.xpath("//table[@class='tableFile']/tr[2]/td[3]/a/@href")[0]
		yield r

def get_ciks_for_name(n) :
	d=requests.post("http://www.sec.gov/cgi-bin/cik.pl.c",data={ "company" : n })
	try :
		t=etree.fromstring(d.content,etree.HTMLParser())
		r={"query" : n, "results" : t.xpath("//p/strong/text()|//p/b/text()")[0] }
		r["list"]=zip(t.xpath("//pre[2]/a/text()"),t.xpath("//pre[2]/text()")[1:])
	except Exception, e :
		logger.error("Error getting ciks for %s:%s" % (n,e))
		r={ 'list' : [] }
	
	return r


cikdb={}

def nqs_for_name(n) :
	r=get_ciks_for_name(n)
	logger.debug("%s ciks for '%s'" % (len(r),n))
	for l in r["list"] :
		comp=dict(cik=l[0],name=l[1][:-1])
		if not comp["cik"] in cikdb :
			cikdb[comp["cik"]]=comp
			for a in get_nq_for_cik(comp["cik"]) :
				a.update(comp)
				yield a

def save_to_store(nq) :
	logger.info("storing %(date)s %(cik)s %(name)s" % nq)
	try :
		store.insert(nq,"docs")
	except Exception, e:
		logger.error("failed to store %s:%s" % (repr(nq),e)) 
		
	




if __name__ == '__main__'  : 
	for a in ("( 0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m mu n o p q r s t u v w x y z").split(" ") :
		for nq in nqs_for_name("blackrock %s" % a) :
			save_to_store(nq)
	for nq in nqs_for_name("ishares") :
		save_to_store(nq)
