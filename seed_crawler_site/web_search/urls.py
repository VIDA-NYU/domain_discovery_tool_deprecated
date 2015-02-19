from django.conf.urls import patterns, url

from web_search import views

urlpatterns = patterns('',
    url(r'^$', views.get_query, name='get_query'),
)
