from django.conf import settings

RTV_FEDORA_HOST = getattr(settings,'RTV_FEDORA_HOST', 'http://localhost:8080')
RTV_FEDORA_CONTEXT = getattr(settings,'RTV_FEDORA_CONTEXT', 'fedora')
RTV_FEDORA_USER = getattr(settings,'RTV_FEDORA_USER', 'fedoraAdmin')
RTV_FEDORA_PASSWORD = getattr(settings,'RTV_FEDORA_PASSWORD', 'fedoraAdmin')
RTV_PID_NAMESPACE = unicode(getattr(settings, 'RTV_PID_NAMESPACE', 'rtv'))

RTV_FFMPEG = getattr(settings, 'RTV_FFMPEG', '/usr/bin/ffmpeg')
RTV_FFMPEG2THEORA = getattr(settings, 'RTV_FFMPEG2THEORA', 
    '/usr/bin/ffmpeg2theora')

FEDORA_INSTANCE = RTV_FEDORA_HOST+'/'+RTV_FEDORA_CONTEXT

class ConfigurationError(Exception):pass
from subprocess import check_call

def check_bins():
    """
    Runs check_call on required binaries for the system.
    Configure settings.RTV_FFMPEG and settings.RTV_FFMPEG2THEORA to control 
    their locations.
    """
    try:
        check_call([RTV_FFMPEG, '-version'])
    except OSError:
        raise ConfigurationError('Unable to call ffmpeg at [%s]' % RTV_FFMPEG)
    try:
        check_call([RTV_FFMPEG2THEORA])
    except OSError:
        raise ConfigurationError('Unable to call ffmpeg2theora at [%s]' % 
            RTV_FFMPEG2THEORA)
        
