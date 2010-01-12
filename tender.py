import urllib2, math
from base64 import b64encode
from datetime import datetime, timedelta
from time import strptime

from multipass import MultiPass
from template_parser import URITemplate

try:
    from django.utils import simplejson
except ImportError:
    import simplejson

def build_url(url_template, values=None):
    '''Builds url from template and dict of values'''
    if not values:
        values = {}
    else:
        #make sure that values are strings
        for x in values:
            values[x] = str(values[x])
    
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
    
class TenderCollection(list):
    def __init__(self, client, url_template, klass, list_key):
        self.client = client #TenderClient instance
        self.url_template = url_template #template of item list url
        self.klass = klass #class to instanciate each object in list
        self.list_key = list_key #key in response dict, that holds item list
        self = self._load_items()
        
    def _load_items(self):
        url = build_url(self.url_template)
        
        resource = self.client.__get__(url)
        #add items from first page
        self._add_to_list(resource.get(self.list_key))
        
        self.total, self.per_page = resource.total, resource.per_page
        
        #how many pages are there
        pages = int(math.ceil( float(self.total) / float(self.per_page) ))
        
        #get all needed pages and build complete list (remember we already have first page)
        for page in xrange(2, pages + 1):
            url = build_url(self.url_template, {'page': page})
            self._add_to_list(self.client.__get__(url).get(self.list_key))
    
    def _add_to_list(self, items):
        '''Adds each item from items to self'''
        self.extend([self.klass(self.client, raw_data = ResponseDict(x)) for x in items])
    
    def count(self):
        return self.total

class TenderResource(object):
    '''Any resource like category, discussion, comment
    Loads itself from give resource_href if no raw_data given'''
    
    def __init__(self, client, resource_href=None, raw_data=None):
        self.client = client
        
        if not raw_data:
            self.raw_data = self.client.__get__(resource_href)
        else:
            self.raw_data = raw_data
    
    @property
    def href(self):
        try:
            return self.raw_data.html_href
        except AttributeError:
            return None
    
    def do_action(self, action_name, **kwargs):
        action_key = action_name + '_href'
        if action_key in self.raw_data:
            url = build_url(self.raw_data[action_key], kwargs)
            #stub data to make urllib2 use POST
            return self.client.__get__(url, data='post') 
        else:
            raise AttributeError('Unknown action')
    
class TenderUser(TenderResource):
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
        return TenderCollection(self.client, self.raw_data.discussions_href, TenderDiscussion, 'discussions')

class TenderDiscussion(TenderResource):
    def fetch_more(self):
        ''' if this discussion is from a list, this function 
        will fetch things like the comments that are only available when
        getting a discussion by itself'''
        self.raw_data = self.client.__get__(self.raw_data.href)
    
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
    def category(self):
        return TenderCategory(self.client, self.raw_data.category_href)

    @property
    def is_public(self):
        return self.raw_data.public

    def comments(self):
        if 'comments' not in self.raw_data:
            self.fetch_more()
        
        comments = []
        for raw_comment in self.raw_data.comments:
            comments.append(TenderComment(self.client, raw_data=ResponseDict(raw_comment)))
        return comments

    # action shortcuts
    
    def toggle(self):
        self.raw_data = self.do_action('toggle')
        if self.is_public == True:
            return u'Public'
        return u'Private'
    
    def resolve(self):
        self.raw_data = self.do_action('resolve')
    
    def unresolve(self):
        self.raw_data = self.do_action('unresolve')
    
    def acknowledge(self):
        self.raw_data = self.do_action('acknowledge')

    def change_category(self, category_id=None):
        self.raw_data = self.do_action('change_category', category_id=category_id)
        return self.category

class TenderComment(TenderResource):
    @property
    def number(self):
        return self.raw_data.number

    @property
    def formatted_body(self):
        return self.raw_data.formatted_body

    @property
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

class TenderCategory(TenderResource):
    @property
    def id(self):
        return int(self.raw_data.href.split('/')[-1])

    @property
    def name(self):
        return self.raw_data.name
    
    @property
    def permalink(self):
        return self.raw_data.permalink
    
    @property
    def formatted_summary(self):
        return self.raw_data.formatted_summary

    @property
    def summary(self):
        return self.raw_data.summary
    
    @property
    def public(self):
        return self.raw_data.public
    
    @property
    def accept_email(self):
        return self.raw_data.accept_email
    
    def discussions(self, page=None, state=None, user_email=None):
        return TenderCollection(self.client, self.raw_data.discussions_href, TenderDiscussion, 'discussions')
        
    def create_discussion(self, title, body, author_email=None, public=True, **kwargs):
        return self.client.create_discussion(self, title, body, self.id, author_email=None, public=True, **kwargs)

class TenderQueue(object):
    pass

class TenderSection(object):
    pass

class TenderClient(object):
    def __init__(self, app_name, secret, user_email, user_id=None):
        self.user_email = user_email
        self.user_id = user_id
        self.app_name = app_name
        self.secret = secret
        
        self.raw_data = self.__get__('http://api.tenderapp.com/%s' % app_name)
        
        self.href = self.raw_data.href
    
    def multipass(self, expires=None, username=None, email=None, unique_id=None, trusted=True, avatar_url=None, alternate_id=None, **kw):
        '''
            takes required (any any number of extra) args and creates a multipass url
            for loggin a user into tender using your sites login.
            
            username: the name of the user being logged in
            email: the email of the user being logged in
            unique_id: a unique id for this user (in case their name or email changes)
            expires: time--in seconds--to keep a user logged into tender
            trusted: if the spam filter should be bypassed
            avatar_url: image to use for this users avatar
            extras: anything else you may want to display about the user
            
            via https://help.tenderapp.com/faqs/setup-installation/multipass
        '''
        data = {
            'email': email or self.user_email,
            'expires': (datetime.now()+timedelta(seconds=expires or 1209600)).strftime("%Y-%m-%dT%H:%M"),
            'trusted': trusted
        }
        if unique_id or self.user_id:
            data['unique_id'] = unique_id or self.user_id
        data.update(kw)
        
        print data
        
        return MultiPass(self.app_name, self.secret).encode(data)
    
    def multipass_url(self, tender_url, multipass):
        return 'http://%s?sso=%s' % (tender_url, multipass)
    
    def profile(self):
        return TenderUser(self, self.raw_data.profile_href)

    def discussions(self, page=None, state=None, category=None, user_email=None):
        return TenderCollection(self, self.raw_data.discussions_href, TenderDiscussion, 'discussions')
    
    def categories(self, page=None):
        return TenderCollection(self, self.raw_data.categories_href, TenderCategory, 'categories')
    
    def users(self):
        return TenderCollection(self, self.raw_data.users_href, TenderUser, 'users')

    def create_discussion(self, title, body, category_id, author_email=None, public=True, **kwargs):
        '''
        creates discussion inside this category
        any additional data can be passed in keyword args
        '''
        url = build_url(self.raw_data['categories_href']) + '/%s/discussions' % category_id
        
        payload = {
            'author_email': author_email or self.client.user_email,
            'title':title,
            'body':body,
            'public':public
        }
        
        #additional arguments
        payload.update(kwargs)
        
        return TenderDiscussion(self, raw_data=self.__get__(url, payload))
    
    # The stuff that does the work...
    def _send_query(self, url, data=None):
        '''
        Send a query to Tender API
        '''
        req = urllib2.Request(url=url)
        req.add_header('Accept', 'application/vnd.tender-v1+json')
        req.add_header('X-Multipass', self.multipass())
        
        if data:
            req.add_header('Content-Type', 'application/json')
            req.add_data(simplejson.dumps(data))
        
        f = urllib2.urlopen(req)
        return f.read()
    
    def __get__(self, url, data=None):
        response = self._send_query(url, data)
        return ResponseDict(simplejson.loads(response))

