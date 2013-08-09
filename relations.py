from scraper.littlesis import LittleSisBrowser,writeXML
import logging
import os,sys
import shelve 
from lxml.builder import E

logging.basicConfig(level=logging.DEBUG,file=sys.stderr)
logger=logging.getLogger(os.path.split(__file__)[1])



persid="37085"

# 
url="http://api.littlesis.org/entity/%s/related/degree2.xml?cat1_ids=8&cat2_ids=8&num=100&page=%%i" % persid

output="output/littlesis/lawrence_fink_%s_network_lobbying_%%04i.xml" % persid
cache="data/littlesisids.db"
idcache=shelve.DbfilenameShelf(cache)
b=LittleSisBrowser()

def id_to_url(ids) :
	if not ids in idcache :
		e=b.tree("http://api.littlesis.org/entity/%s.xml" % ids)
		logger.debug("%s -> %s" % (ids,e.xpath("//uri/text()")[0]))
		idcache[ids]=str(e.xpath("//uri/text()")[0])
	return idcache[ids]


page=1

while True :
	of=output % page
	iu=url % page
	t=b.tree(iu)
	count=int(t.xpath("//Meta/ResultCount/Degree2Entities/text()")[0])
	logger.debug("Page %s : %s entities" % (page,count))
	for ent in t.xpath("//Degree2Entities/Entity") :
		idt=ent.xpath(".//degree1_ids/text()")[0]
		for tti in idt.split(",") :
			u=id_to_url(tti)
			el=E.degree1_url(u)
			ent.append(el)
	writeXML(t,of)
	page=page+1
	if (count<100) :
		break

