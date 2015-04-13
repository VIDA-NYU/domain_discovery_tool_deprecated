from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
import settings

urlpatterns = [
    # Examples:
    # url(r'^$', 'seed_crawler_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^web_search/', include('web_search.urls')),
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

