import urllib2
from base64 import b64encode

try:
    from django.utils import simplejson
except ImportError:
    import simplejson

class ResponseDict(dict):
    ''' Simple wrapper of dict object, gives access to dict keys as properties'''
    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

class TenderClient(object):
    def __init__(self, app_name, user, password):
        self.user = user
        self.password = password
        
        self.values = self.__get__('http://api.tenderapp.com/%s' % app_name)
        
        self.href = self.values.herf
    
    def discussions(self, page=None, state=None, category=None, user_email=None):
        raw_discussions = self.__get__(self.values.discussions_href)
        
        # here raw discussion need to be turned into a list of TenderDiscussion objects
    
    def categories(self, page=None):
        raw_categories = self.__get__(self.values.categories_href)
        
        # here raw discussion need to be turned into a list of TenderDiscussion objects
    
    def users():
        pass
    
    def profile(self):
        pass

    # The stuff that does the work...
    def _send_query(self, url, data=None):
        '''
        Send a query to Tender API
        '''
        
        req = urllib2.Request(url=url)
        req.add_header('Accept', 'application/vnd.tender-v1+json')
        req.add_header(
            'Authorization', 'Basic %s' % b64encode('%s:%s' % (self.user, self.password))
        )
        if data:
            req.add_header('Content-Type', 'application/json')
            req.add_data(simplejson.dumps(data))
        
        #print req.get_method(), req.get_data(), req.get_full_url()
        
        f = urllib2.urlopen(req)
        return f.read()
    
    def __get__(self, url):
        response = self._send_query(url)
        return ResponseDict(simplejson.loads(response))

class TenderObject(object):
    def __init__(self,client):
        self.client = client

class TenderProfile(TenderObject):
    pass
class TenderDiscussion(TenderObject):
    pass
class TenderCategory(TenderObject):
    pass
class TenderUser(TenderObject):
    pass
class TenderQueue(TenderObject):
    pass
class TenderSection(TenderObject):
    pass