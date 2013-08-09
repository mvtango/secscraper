import os
import requests
import requests_cache
import time
import logging
import sys
from requests_cache import CachedSession

logger=logging.getLogger(__name__)

_here=os.path.split(__file__)[0]
if not _here in sys.path:
	sys.path.append(_here) 

requests_cache.install_cache(os.path.join(_here,"cache","requests_cache"))

def throttle_hook(request,**kwargs) :
	if hasattr(request,"from_cache") and request.from_cache:
		pass
	else : 
		time.sleep(1)
		



class Browser(CachedSession) :
	
	def __init__(self,*args,**kwargs) :
		super(Browser, self).__init__()
		self._init={ "args" : args, "kwargs" : kwargs }
		
		
	def request(self,*args,**kwargs) :
		kwargs.update(self._init["kwargs"])
		return CachedSession.request(self,*args,**kwargs)

		

browser=Browser(hooks={ 'response' : throttle_hook })
browser.headers.update({'Accept-Language' : 'de-de,de,en,es', 
   			'Accept-Charset' :'utf-8', 
			'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5'})



