import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase

from tenderize.api import Client
from tenderize.helpers import tender_hash, tenderize_response
from tenderize.views import login_and_tenderize


class TenderizeTest(TestCase):
    urls = 'tenderize.tests.test_urls'
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'templates'),
    ]

    def setUp(self):
        # Template nessecary to test login.
        self.old_template_dir = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = self.template_dirs

        self.tclient = Client(user=settings.TENDER_EMAIL, password=settings.TENDER_PASSWORD)

        self.user = 'user'
        self.email = 'user@gmail.com'
        self.password = 'password'
        self.tender = 'help.yourapp.com'
        self.expires = 1228117891
        self.secret = 'monkey'
 
    def tearDown(self):
        settings.TEMPLATE_DIRS = self.old_template_dir

    def testTenderHash(self):
        result = tender_hash(self.email, self.expires, self.tender, self.secret)
        self.assertEquals(result, '1937bf7e8dc9f475cc9490933eb36e5f7807398a')

    def testTenderizeResponse(self):
        # Tenderized response will contain Tender cookies.
        response = HttpResponse('Test Response')
        response = tenderize_response(response, self.email, {'user': self.user})
        self.assertEqual(response.cookies['tender_email'].value, self.email)
        self.assertEqual(response.cookies['tender_user'].value, self.user)
        self.assertTrue('tender_expires' in response.cookies)
        self.assertTrue('tender_hash' in response.cookies)
                
    def testLoginAndTenderize(self):
        user = User.objects.create_user(self.user, self.email, self.password)
        
        # Correct login returns HttpResponseRedirect
        login = reverse('login_and_tenderize')
        data = {'username': self.user, 'password': self.password}
        response = self.client.post(login, data)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertTrue('tender_expires' in response.cookies)
        self.assertTrue('tender_hash' in response.cookies)
        self.assertTrue('tender_email' in response.cookies)
        
        # Bad login returns HttpResponse
        bad_data = {'username': self.user, 'password': 'monkey'}
        response = self.client.post(login, bad_data, follow=False)
        self.assertTrue(isinstance(response, HttpResponse))

    # API Tests

    def test_get_categories(self):
        result = self.tclient.get_categories()

        keys = (u'per_page', u'total', u'categories', u'offset')

#        import pprint
#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(result)

        for k in keys:
            assert result.has_key(k)

            if k == 'categories':
                for category in result[k]:
                    for ck in ('discussions_href', 'href', 'last_updated_at',
                                'name', 'permalink'):
                        assert category.has_key(ck)

    def test_get_discussions(self):
        result = self.tclient.get_discussions()

#        import pprint
#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(result)

        keys = (u'per_page', u'total', u'discussions', u'offset')
        for k in keys:
            assert result.has_key(k)

            if k == 'discussions':
                for discussion in result[k]:
                    for dk in ('author_email', 'author_name', 'category_href',
                                'comments_count', 'comments_href', 'created_at',
                                'href', 'last_author_email', 'last_author_name',
                                'last_comment_id', 'last_updated_at',
                                'last_user_id', 'last_via', 'number',
                                'permalink', 'public', 'resolve_href', 'state',
                                'title', 'toggle_href', 'via'):
                        assert discussion.has_key(dk)

#    def test_get_queues(self):
#        result = self.tclient.get_queues()

#        import pprint
#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(result)