# coding: utf-8
from dumptruck import DumpTruck
import csv,os,glob

_here=os.path.split(__file__)[0]

store=DumpTruck(dbname="db/documents.db")

already=dict([(a[26:36],a) for a in [os.path.split(a)[1] for a in glob.glob("/home/martin/Dropbox/blackrock-scraper/data/*")]])

already_downloaded=dict([(a[26:36],a) for a in [os.path.split(a)[1] for a in glob.glob(os.path.join(_here,"data/html/*"))]])

print len(already_downloaded.items()),len(already.items())
#s
#
# Liste aller Gesellschaften mit aktuellstem Berichtsdatum und Anzahl der Berichte
dt=csv.DictWriter(open(os.path.join(_here,"data/tables","ciks.csv"),"w"),['act','num','cik','name','filename','already','already_downloaded','exists','link'],delimiter=";")
dt.writerow(dict(act="Aktuellster Bericht",num="Anzahl der Berichte",cik="Central Index Key",name="Name",already='frühere analysiert?', already_downloaded='frühere heruntergeladen?', exists='vorhanden?',filename='Aktuellster Bericht (lokal)',link="Aktuellster Bericht (Internet)"))
for o in store.execute("select cik,name,count(date) as num,max(date) as act from docs group by cik order by act desc") :
	details=store.execute("select date,cik,doc from docs where cik='%s' order by date desc limit 1" % o["cik"])[0]
	o["link"]=details["doc"]
	details["fn"]=os.path.split(details["doc"])[1]
	o["filename"] = "%(date)s-%(cik)s-%(fn)s" % details
	o["exists"]=os.path.exists(os.path.join("/home/martin/Dropbox/blackrock-scraper/data",o["filename"]))
	if not o["exists"] :
		o["already"]="ea:%s" % already.get(o["cik"],'none analyzed')
		o["already_downloaded"]="ed:%s" % already.get(o["cik"],'none downloaded')
	else :
		o.update(dict(already='',already_downloaded=''))
	dt.writerow(o)

