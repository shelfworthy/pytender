import unittest

from tender import Client

TENDER_APP = ''
USER_EMAIL = ''
USER_PASSWORD = ''

class TenderTest(unittest.TestCase):
    def setUp(self):
        self.tclient = Client(app_name=TENDER_APP, user=USER_EMAIL, password=USER_PASSWORD)

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