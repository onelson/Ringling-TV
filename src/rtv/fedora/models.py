"""
It is vitally important that you understand the models in this module are *NOT*
conventional django models.  These classes provide a high-level access layer to
objects stored in your fedora repository.  Where possible, they will emulate 
django's orm, but that is only the influence for the interface - not the 
storage.  Tread carefully when using these classes.
"""

from rtv.settings import RTV_PID_NAMESPACE
from rtv.fedora import NS, pp, get_client

class FedoraObject(object):
    pid = None
    datastreams = None
    @staticmethod
    def create(*args, **kwargs):
        raise NotImplementedError
    @staticmethod
    def purge(*args, **kwargs):
        raise NotImplementedError


class FedoraDataStream(object):
    def __init__(self):
        pass
    def __get__(self, instance, owner): 
        raise NotImplementedError
    def __set__(self, instance, value): 
        raise NotImplementedError
    def __del__(self, instance): 
        raise NotImplementedError
    

class Video(FedoraObject):
    user = None
    pid = None
    title = None
    client = None
    fcobj = None
    
    @staticmethod
    def create(*args, **kwargs):pass
    @staticmethod
    def purge(*args, **kwargs):pass
    
    def __init__(self, pid=None):
        self._client = get_client()
        self.pid = pid
        if self.pid:
            self.fcobj = self._client.getObject(self.pid)
    
    def _load(self):
        self.fcobj = self._client.getObject(self.pid)

    def _new(self):
        self.pid = self._client.getNextPid(RTV_PID_NAMESPACE)
        obj = self._client.createObject(self.pid, label=self.title)
        obj.addDataStream(u'RELS-EXT')
        rels = obj['RELS-EXT']
        rels[NS.rdfs.hasModel].append(dict(
            type = u'uri',
            value = u'info:fedora/'+pp('EPISODE')
        ))
        rels.checksumType = u'DISABLED'
        rels.setContent()
