from lxml import etree 
import requests
parser=etree.HTMLParser()

def getTree(url) :
	return etree.parse(url,etree.HTMLParser())



def get_nq_for_cik(cik) :
	tree=getTree("http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=N-Q%%25&dateb=&owner=include&start=0&count=40&output=atom" % cik)
	for entry in tree.xpath("//entry") :
		link=entry.xpath("link/@href")[0]
		date=entry.xpath("updated/text()")
		r={"date" : date, "link" : link }
		stree=getTree(link)
		r["doc"]="http://www.sec.gov/%s" % stree.xpath("//table[@class='tableFile']/tr[2]/td[3]/a/@href")[0]
		yield r

def get_ciks_for_name(n) :
	d=requests.post("http://www.sec.gov/cgi-bin/cik.pl.c",data={ "company" : n })
	t=etree.fromstring(d.content,etree.HTMLParser())
	r={"query" : n, "results" : t.xpath("//p/strong/text()|//p/b/text()")[0] }
	r["list"]=zip(t.xpath("//pre[2]/a/text()"),t.xpath("//pre[2]/text()")[1:])
	return r

if __name__ == '__main__'  : 
	import pprint
	# pprint.pprint([a for a in get_nq_for_cik("0001026144")])
	for a in ("a b c d e f g h i j k l m mu n o p q r s t u v w x y z").split(" ") :
		r=get_ciks_for_name("blackrock %s" % a)
		for l in r["list"] :
			print "\t".join([l[0],l[1][:-1],r["results"],r["query"]])
	
