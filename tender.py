import urllib2
from base64 import b64encode
from datetime import datetime
from time import strptime

from template_parser import URITemplate

try:
    from django.utils import simplejson
except ImportError:
    import simplejson

def build_url(url_template, values={}):
    '''Builds url from template and dict of values'''
    return URITemplate(url_template).sub(values)
    
def date_from_string(string):
    return datetime(*strptime(string, '%Y-%m-%dT%H:%M:%SZ')[:6])

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
        
        self.href = self.values.href
    
    def profile(self):
        return TenderUser(self, self.values.profile_href)

    def discussions(self, page=None, state=None, category=None, user_email=None):
        url = build_url(self.values.discussions_href)
        raw_discussions = self.__get__(url)
        
        return raw_discussions.discussions
    
    def categories(self, page=None):
        raw_categories = self.__get__(self.values.categories_href)
        
        # here raw discussion need to be turned into a list of TenderDiscussion objects
    
    def users(self):
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

class TenderUser(object):
    def __init__(self, client, user_href):
        self.client = client
        
        self.raw_data = self.client.__get__(user_href)

    @property
    def email(self):
        return self.raw_data.email

    @property
    def name(self):
        return self.raw_data.name

    @property
    def state(self):
        return self.raw_data.state

    @property
    def title(self):
        return self.raw_data.title or None

    @property
    def created_at(self):
        return date_from_string(self.raw_data.created_at)

    @property
    def activated_at(self):
        return date_from_string(self.raw_data.activated_at)

    @property
    def updated_at(self):
        return date_from_string(self.raw_data.updated_at)

    def discussions(self, page=None, state=None, category=None, user_email=None):
        # this should return a list of discussion items based on the paramiters
        pass

class TenderDiscussion(object):
    def __init__(self, client, discussion_href=None):
        self.client = client
        self.raw_data = self.client.__get__(user_href)
        
        if discussion_href:
            self.is_complete = False
        else:
            self.is_complete = True
            

    def fetch_more(self):
        ''' if this discussion is from a list, this function 
        will fetch things like the comments that are only available when
        getting a discussion by itself'''
        self.raw_data = self.client.__get__(self.raw_data.href)
        self.is_complete = True

    @property
    def number(self):
        return self.raw_data.number

    @property
    def title(self):
        return self.raw_data.title

    @property
    def user(self):
        return TenderUser(self.client, self.raw_data.user_href)

    @property
    def public(self):
        return self.raw_data.public

    def comments(self):
        if not self.is_complete:
            self.fetch_more()
        comments = []
        for raw_comment in self.raw_data.comments:
            comments.append(TenderComment(self.client, raw_comment))
        return comments

class TenderComment(object):
    def __init__(self, client, raw_comment):
        self.client = client
        self.raw_data = raw_comment

    @property
    def number(self):
        return self.raw_data.number

    def body(self):
        return self.raw_data.body
    @property
    def via(self):
        return self.raw_data.via

    @property
    def user(self):
        return TenderUser(self.client, self.raw_data.user_href)

    @property
    def user_is_supporter(self):
        return self.raw_data.user_is_supporter

    @property
    def resolution(self):
        return self.raw_data.resolution

    @property
    def created_at(self):
        return date_from_string(self.raw_data.created_at)

class TenderCategory(object):
    pass
class TenderQueue(object):
    pass
class TenderSection(object):
    pass