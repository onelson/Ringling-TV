
from django.conf.urls.defaults import patterns, include, handler500
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

handler500 # Pyflakes

urlpatterns = patterns(
    '',
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^rtv/', include('rtv.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url':'/rtv/'})
)

if settings.SERVE_STATIC_MEDIA:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )