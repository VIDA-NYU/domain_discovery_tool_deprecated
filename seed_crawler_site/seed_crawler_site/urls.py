from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'seed_crawler_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^test_polls/', include('test_polls.urls')),
    url(r'^web_search/', include('web_search.urls')),
    url(r'^thanks/', include('thanks.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

