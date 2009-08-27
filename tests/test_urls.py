from django.conf.urls.defaults import *
  
urlpatterns = patterns('tenderize.views',
    url(r'^login_and_tenderize/$', 'login_and_tenderize', name="login_and_tenderize"),
)