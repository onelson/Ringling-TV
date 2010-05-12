from django.conf import settings

RTV_FEDORA_HOST = getattr(settings,'RTV_FEDORA_HOST', 'http://localhost:8080')
RTV_FEDORA_CONTEXT = getattr(settings,'RTV_FEDORA_CONTEXT', 'fedora')
RTV_FEDORA_USER = getattr(settings,'RTV_FEDORA_USER', 'fedoraAdmin')
RTV_FEDORA_PASSWORD = getattr(settings,'RTV_FEDORA_PASSWORD', 'fedoraAdmin')
RTV_PID_NAMESPACE = getattr(settings, 'RTV_PID_NAMESPACE', 'rtv')

FEDORA_INSTANCE = RTV_FEDORA_HOST+'/'+RTV_FEDORA_CONTEXT