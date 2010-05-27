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
from django.core.urlresolvers import reverse
import json

class FedoraObjectSet(object):
    """
    Iterator for looping over a sequence of FedoraObjects.  
    Not fully implemented at this point - and therefore not in use.
    """
    def __init__(self, klass, data):
        self.klass = klass
        self.data = data
        self.index = 0
    
    def index(self, i):
        return self.data[i]
    
    def __iter__(self):
        return self
    def next(self):
        self.index = self.index + 1
        try:
            return self.klass(pid=self.data[self.index])
        except IndexError:
            self.index = 0
            raise StopIteration
    def __str__(self): 
        return str(list(self.data))
    def __nonzero__(self):
        return bool(self.data)
    def __len__(self): return len(self.data)


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
        client.deleteObject(unicode(pid))
    @staticmethod
    def get(**kwargs):
        raise NotImplementedError

class FedoraObject(object):
    """
    An abstract base class for fedora objects.
    """
    _pid = None
    _fcobject_cache = None
    objects = FedoraObjectManager()
    __datastreams__ = []
    
    def _get_pid(self):
        return self._pid
    def _set_pid(self, value):
        self._pid = unicode(value)
    def _del_pid(self):
        self._pid = None
        self._fcobject_cache = None
    pid = property(_get_pid, _set_pid, _del_pid)
    
    @property
    def __fcobj__(self):
        if not self._fcobject_cache:
            fc = get_client()
            self._fcobject_cache = fc.getObject(self.pid)
        return self._fcobject_cache 
    
    @property
    def datastreams(self):
        return self.__fcobj__.datastreams()
    
    def _to_fedora(self):
        """
        Should return a set of nested dicts that can be passed directly to the
        object manager for insert/update.
        """
        raise NotImplementedError
    
    def _bind(self, pid=None, **kwargs):
        """
        Maps a dict of fedora data to the object properties.
        """
        raise NotImplementedError
    
    def __init__(self, pid=None, **kwargs):
        if pid:
            self.pid = unicode(pid)
        if kwargs:
            self._bind(**kwargs)
    
    def save(self):
        client = get_client()
        try:
            client.getObject(self._pid)
            self.objects.update(**self._props_to_fedora())
        except FedoraConnectionException:
            self.objects.create(**self._props_to_fedora())
            
    def delete(self):
        self.objects.purge(self.pid)
    def __unicode__(self):
        return unicode('<FedoraObject: %s>' % (self.pid  or 'undefined'))
    def __str__(self): 
        return str(self.__unicode__())
    
class VideoObjectManager(FedoraObjectManager):
    __cmodel__ = u'info:fedora/'+pp('EPISODE')
    @staticmethod
    def create(user, raw, raw_info, mp4, ogv, thumbnail, dc={}):
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
            for key in dc:
                dcore[key] = [unicode(dc[key])]
            dcore.setContent()
        # info on raw media
        obj.addDataStream('RAW_INFO', raw_info, controlGroup=u'M', 
                                 label=u'source media info', mimeType=u'text/plain',
                                 checksumType=u'DISABLED', versionable=False)
        info = obj['RAW_INFO']
        info.setContent()
        # media datastreams
        dstreams = (
            # datastream name, url, mimetype
            ('RAW', raw, u'application/octet-stream', u'R'),
            ('MP4', mp4, u'video/mp4', u'R'),
            ('OGV', ogv, u'video/ogv', u'R'),
            ('THUMBNAIL', thumbnail, u'image/jpeg', u'R')
        )
        for (dsname, url, mime, cgroup) in dstreams:
            obj.addDataStream(dsname, controlGroup=cgroup,
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
    def all():
        fc = get_client()
        sparql = '''prefix rdfs: <%s>
        select ?s where {?s rdfs:hasModel <%s>.}
        ''' % (NS.rdfs, VideoObjectManager.__cmodel__)
        result = fc.searchTriples(sparql)

        pids = []
        for r in result:
            pids.append(unicode(r['s']['value'].replace('info:fedora/','')))
        vids = [Video(pid) for pid in pids]
        return vids
    
    @staticmethod
    def get(**kwargs):
        fc = get_client()
        subqueries = []
        fields = kwargs.keys()
        for k,v in kwargs.iteritems():
            subqueries.append(''.join([k,'~',v]))
        query = unicode(' '.join(subqueries))
        results = [obj for obj in fc.searchObjects(query, fields)]
        if len(results) > 1: 
            raise MultipleResultsError('Search yielded %d results' % len(results))
        elif len(results) == 0:
            raise ObjectNotFoundError('The search "%s" yielded 0 results' % query)
        return Video(pid=results[0]['pid'])

class MultipleResultsError(Exception):pass
class ObjectNotFoundError(Exception):pass

class Video(FedoraObject):
    objects = VideoObjectManager()
    def _bind(self, pid=None, **kwargs):pass
    def _new(self):pass
    def __unicode__(self):
        return unicode('<Video: %s>' % (self.pid  or 'undefined'))
    def __str__(self): 
        return str(self.__unicode__())
    
    @property
    def thumbnail(self):
        return self.__fcobj__['THUMBNAIL'].location
    @property
    def ogv(self):
        return self.__fcobj__['OGV'].location
    @property
    def mp4(self):
        return self.__fcobj__['MP4'].location
    @property
    def raw(self):
        return self.__fcobj__['RAW'].location

    def get_absolute_url(self):
        return reverse('rtv:video_detail', kwargs={'pid': self.pid })
    @property
    def raw_info(self):
        return self.__fcobj__['RAW_INFO'].getContent().read()
    def get_info(self):
        return json.loads(self.raw_info)
    @property
    def width(self):
        return int(self.get_info()['video'][0]['width'])
    @property
    def height(self):
        return int(self.get_info()['video'][0]['height'])
    @property
    def dc(self):
        return self.__fcobj__['DC']
    @property
    def dc_as_dict(self):
        return dict(self.dc)
