from django.conf.urls import patterns, url

from thanks import views

urlpatterns = patterns('',
    url(r'^$', views.show_thanks, name='show_thanks'),
)

