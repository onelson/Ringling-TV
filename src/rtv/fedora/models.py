"""
It is vitally important that you understand the models in this module are *NOT*
conventional django models.  These classes provide a high-level access layer to
objects stored in your fedora repository.  Where possible, they will emulate 
django's orm, but that is only the influence for the interface - not the 
storage.  Tread carefully when using these classes.
"""

from rtv.settings import RTV_PID_NAMESPACE
from rtv.fedora import NS, pp, get_client
from fcrepo.connection import FedoraConnectionException

class FedoraObjectSet(object):
    """
    Iterator for looping over a sequence of FedoraObjects
    """
    def __init__(self, data):
        self.data = data
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index == len(self.data):
            raise StopIteration
        self.index = self.index + 1
        return self.data[self.index]
    def __str__(self): 
        return str(list(self.data))


class FedoraDatastream(object):
    _obj = None
    _controlGroup = None
    _versionable = None
    _name = None
    def __init__(self, instance, name, controlGroup, versionable):
        self._obj = instance # reference to the parent object
        self._name = unicode(name)
        self._controlGroup = unicode(controlGroup)
        self._versionable = bool(versionable)
    def get(self, prop):
        """
        Return the value of datastream.prop
        """
        return getattr(self._obj[self._name], prop)
    
    def set(self, prop, val):
        return setattr(self._obj[self._name], prop, val)
    def __unicode__(self):
        return unicode('<FedoraDataStream: %s>' % (self.pk  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())

class FedoraObjectManager(object):
    __cmodel__ = None
    
    @staticmethod
    def create(**kwargs):
        raise NotImplementedError
    @staticmethod
    def update(**kwargs):
        raise NotImplementedError
    @staticmethod
    def purge(pid):
        client = get_client()
        client.deleteObject(pid)
    @staticmethod
    def get(**kwargs):
        raise NotImplementedError
    def __unicode__(self):
        return unicode('<FedoraObjectManager: %s>' % (self.pk  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())

class FedoraObject(object):
    """
    An abstract base class for fedora objects.
    """
    pid = None
    objects = FedoraObjectManager()
    __datastreams__ = []
    
    def _datastream(self, name):
        def _get(name):
            return self.pid
        return property()
    
    def _props_to_fedora(self):
        raise NotImplementedError
    
    def __init__(self, **kwargs):
        if kwargs:
            self._load(**kwargs)
    
    def save(self):
        client = get_client()
        try:
            client.getObject(self.pid)
            is_new = False
        except FedoraConnectionException:
            is_new = True
        if is_new:
            self.objects.create(**self._props_to_fedora())
        else:
            self.objects.update(**self._props_to_fedora())
    def delete(self):
        self.objects.purge(self.pid)
    def __unicode__(self):
        return unicode('<FedoraObject: %s>' % (self.pid  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())
    
class VideoObjectManager(FedoraObjectManager):
    __cmodel__ = u'info:fedora/'+pp('EPISODE')
    __datastreams__ = ['DC', 'RELS-EXT', 'MP4', 'OGV', 'THUMBNAIL']
    @staticmethod
    def create(user, raw, mp4, ogv, thumbnail, dc={}):
        fc = get_client()
        pid = fc.getNextPID(RTV_PID_NAMESPACE)
        
        obj = fc.createObject(pid, label=unicode(dc['title']))
        obj.addDataStream(u'RELS-EXT')
        rels = obj['RELS-EXT']
        rels[NS.rdfs.hasModel].append(dict(
            type = u'uri',
            value = VideoObjectManager.__cmodel__
        ))
        rels.checksumType = u'DISABLED'
        rels.setContent()
        if dc:
            dcore = obj['DC']
            dcore.versionable = False
            for k, v in dc.iteritems():
                dcore[k] = unicode(v)
            dcore.setContent()
        dstreams = (
            ('RAW', raw, u'application/octet-stream'),
            ('MP4', mp4, u'video/mp4'),
            ('OGV', ogv, u'video/ogv'),
            ('THUMBNAIL', thumbnail, u'image/jpeg')
        )
        for (dsname, url, mime)in dstreams:
            obj.addDataStream(dsname, controlGroup=u'R',
                                            label = u'media ds', 
                                            logMessage = u'adding ds',
                                            location = unicode(url),
                                            mimeType = mime,
                                            checksumType= u'DISABLED',
                                            versionable = False)
            
#            These 2 lines basically commit the change to the fedora object, 
#            which helps us avoid getting object locked errors when adding 
#            numerous datastreams to an object in a short period of time.
            
            ds = obj[dsname]
            ds.setContent()
        
        return VideoObjectManager.get(pid=pid)
            
    @staticmethod
    def get(**kwargs): pass
    def __unicode__(self):
        return unicode('<VideoObjectManager: %s>' % (self.pid  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())
    
class Video(FedoraObject):
    user = None
    pid = None
    title = None
    objects = VideoObjectManager()

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
    def __unicode__(self):
        return unicode('<Video: %s>' % (self.pid  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())