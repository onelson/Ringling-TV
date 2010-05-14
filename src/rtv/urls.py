from django.conf.urls.defaults import patterns, include, handler500, url
handler500 # Pyflakes

urlpatterns = patterns(
    'rtv.views',
    url(r'^$', 'demo', name='demo_view'),
    url(r'^upload/$', 'upload', name='upload_view'),
    url(r'^success/$', 'success', name='success_view'),
)