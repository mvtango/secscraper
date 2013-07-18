from lxml import etree
import simplejson
import pprint
import re
import string
from unicodecsv import UnicodeWriter
# from processor import GenericProcessor
# process=GenericProcessor()


files={ "in" : [
				"data/d/d538216dnq.htm",
				"data/d/i00449_if-nq.htm",
				"data/d/i00222_if-nq.htm",
				"data/d/i00499_if-nq.htm",
				"data/d/i00242_ifi-nq.htm",
				"data/d/i00001_indexfunds-nqa.htm",
				

		],
        "csv" : "extract.csv" }


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
      "table" : [ "fund","date","category","name","shares","value"]
      
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
	tree=etree.parse(open(fn),etree.HTMLParser())

	data=[]
	props={}
	for (k,v) in parse["properties"].items() :
		props[k]=stringstring(extract(tree,v))
	pprint.pprint(props)
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
				
		data.append(cdata)
		

	# pprint.pprint(map(lambda a:  { "a" : a.get("reaction","-"), "b" : a.get("color",""), "c" : a.get("amendment","") },data));
	print "%s containers\n" % len(data)
	for container in data :
		if len(container)>0 :
			pprint.pprint(container)
			ofile.writerows(container)
			
