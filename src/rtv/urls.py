from django.conf.urls.defaults import patterns, include, handler500, url
handler500 # Pyflakes

urlpatterns = patterns(
    'rtv.views',
    url(r'^$', 'demo', name='index'),
    url(r'^demo/$', 'demo', name='demo'),
    url(r'^upload/$', 'upload', name='upload'),
    url(r'^success/$', 'success', name='success'),
    url(r'^publish-queue/$', 'info', name='queue'),
    url(r'^ingest/(?P<job_id>\d+)/$', 'video_ingest', name='ingest'),
    url(r'^view/(?P<pid>\w+:\d+)/$', 'video_detail', name='video_detail'),
    url(r'^list/$', 'video_list', name='video_list'),
    url(r'^update/(?P<pid>\w+:\d+)/$', 'video_update', name='video_update'),
    url(r'^state/(?P<pid>\w+:\d+)/(?P<state>[A|I|D]{1})/$', 'video_state', name='video_state'),
    url(r'^delete/(?P<pid>\w+:\d+)/$', 'video_delete', name='video_delete'),
)