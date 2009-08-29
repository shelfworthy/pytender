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

	>> len(discussions)
	53

	>> discussions[1].title
	u'discussion title'

	>> discussions[1].public
	True

### And then comments for that discussion

	>> discussions[1].comments()
