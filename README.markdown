Requirements
------------

* python 2.5+
* [tpg](http://christophe.delord.free.fr/tpg/index.html)


Installation
------------

just add tender.py to your python path.

Examples
--------

	>> tender = TenderClient('appname', 'user email', 'user password')

### we can get info on the current user:

	>> tender.profile().name
	u'Chris Drackett'

### dates are converted into datetime objects.

	>> tender.profile().created_at
	datetime.datetime(2009, 8, 26, 21, 28, 5)

### TenderUser can be used to get all the discussions for that user...

	>> discussions = tender.profile().discussions()

	>> discussions.count()
	53

	>> discussions[1].title
	u'discussion title'

	>> discussions[1].public
	True

### And then comments for that discussion

	>> comments = discussions[1].comments()

	>> comments[0].formatted_body
	u'<div><p>this is the comment body</p></div>'

	>> comments[0].user().name
	u'Chris Drackett

	>> comments[0].created_at
	datetime.datetime(2009, 9, 12, 3, 21, 14)

### From the tender API object we can also get categories

	>> all_categories = tender.categories()

	>> all_categories[0].name
	u'Questions'

	>> all_categories[0].summary
	u'Ask us anything!'

	>> question_discussions = all_categories[0].discussions()

	>> question_discussions[0].title
	u'This is a question'