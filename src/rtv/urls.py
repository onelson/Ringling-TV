from django.conf.urls.defaults import patterns, include, handler500, url
handler500 # Pyflakes

urlpatterns = patterns(
    'rtv.views',
    url(r'^$', 'demo', name='demo_view'),
)