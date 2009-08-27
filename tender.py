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

class Client(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        #initial data
        self.site = self.get_sites()

    def _send_query(self, url, data=None):
        '''
        Send a query to Tender API
        '''
        import urllib2
        from base64 import b64encode

        req = urllib2.Request(url=url)
        req.add_header('Accept', 'application/vnd.tender-v1+json')
        req.add_header(
            'Authorization', 'Basic %s' % b64encode(
                '%s:%s' % (self.user, self.password)
            )
        )
        if data:
            req.add_header('Content-Type', 'application/json')
            req.add_data(simplejson.dumps(data))

        #print req.get_method(), req.get_data(), req.get_full_url()

        f = urllib2.urlopen(req)
        return f.read()

    def _parse_response(self, response):
        '''
        Parse JSON response
        '''
        return ResponseDict(simplejson.loads(response))

    def __get__(self, url, data=None):
        response = self._send_query(url, data)
        return self._parse_response(response)

    def get_sites(self):
        return self.__get__('http://api.tenderapp.com/%s' % settings.TENDER_APP_NAME)

    def get_categories(self):
        return self.__get__('http://api.tenderapp.com/%s/categories' % settings.TENDER_APP_NAME)

    def get_discussions(self):
        return self.__get__('http://api.tenderapp.com/%s/discussions' % settings.TENDER_APP_NAME)

    def get_queues(self):
        '''
        Have no idea why but it always returns 401: Unauthorized
        '''
        return self.__get__('http://api.tenderapp.com/%s/queues' % settings.TENDER_APP_NAME)

    def create_discussion(self, data, category=None):
        '''
        Creates a discussion from POST data
        '''
        url = 'http://api.tenderapp.com/%s/categories/10267/discussions' % settings.TENDER_APP_NAME
        #if category:
        #    url = '%s/%s' % (url, category)

        return self.__get__(url, data)
        
    def __getattr__(self, name):
        try:
            return super(Client, self).__getattr__(name)
        except AttributeError:
            return getattr(self.site, name)
            