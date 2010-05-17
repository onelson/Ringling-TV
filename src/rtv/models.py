from django.db import models
from django.db.models.signals import pre_save, post_init
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.files import File
import datetime, os
from uuid import uuid4
import rtv.fedora
from rtv.fedora import u, pp, NS
from rtv.transcoder import theora, h264, jpeg, TranscodeError
from rtv.settings import RTV_PID_NAMESPACE

def upload_dst(instance, filename):
    path_components = [
        'uploads', 'processed', RTV_PID_NAMESPACE]
    path_components += [digit for digit in str(instance.pk)]
    path_components.append(filename)
    return r'%s' % os.path.join(*path_components)

class TranscodeJob(models.Model):

    STATUS_PENDING = 1
    STATUS_PROCESSING = 2
    STATUS_PROCESSED = 3
    STATUS_ERROR = 4
    
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_PROCESSING, 'processing'),
        (STATUS_PROCESSED, 'processed'),
        (STATUS_ERROR, 'error'),
    )
    
    user = models.ForeignKey(User, editable=False)
    title = models.CharField(max_length=100, editable=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, 
                                      default=STATUS_PENDING, editable=False)
    source = models.FileField(upload_to=upload_dst, null=True)
    
    ogv = models.FileField(upload_to=upload_dst, null=True, editable=False)
    mp4 = models.FileField(upload_to=upload_dst, null=True, editable=False)
    thumbnail = models.FileField(upload_to=upload_dst, null=True, editable=False)
    
    created = models.DateTimeField(auto_now_add=True)
    transcoded = models.DateTimeField(null=True, editable=False)
    
    def transcode(self):
        self.status = self.STATUS_PROCESSING
        self.save()
        base = os.path.splitext(os.path.basename(self.source.name))[0]
        try:
            jpg = jpeg(self.source.path)
            self.thumbnail.save(base+'.jpg', File(open(jpg,'rb')))
            
            mp4 = h264(self.source.path)
            self.mp4.save(base+'_h264.mp4', File(open(mp4,'rb')))
            
            ogv = theora(self.source.path)
            self.ogv.save(base+'_theora.ogv', File(open(ogv,'rb')))
            
            self.status = self.STATUS_PROCESSED
            self.transcoded = datetime.datetime.now()
        except TranscodeError:
            self.STATUS_ERROR
        self.save()
        for file in [jpg,mp4,ogv]:
            os.remove(file)

class TranscodeJobForm(ModelForm):
    class Meta:
        model = TranscodeJob

class Video(models.Model):
    user = models.ForeignKey(User, editable=False)
    pid = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=100)
    
    source = models.URLField()
    # derivatives
    ogv = models.URLField()
    mp4 = models.URLField()
    thumbnail = models.URLField()

    created = models.DateTimeField(auto_now_add=True)

    def bind_to_fobject(pid=None):
        fc = rtv.fedora.get_client()
        if pid is not None:
            self.pid = pid
        else:
            self.pid = fc.getNextPid(RTV_PID_NAMESPACE)
            
        try:
            obj = fc.getObject(self.pid)
        except FedoraConnectionException:
            # if create fails, we need to create
            obj = fc.createObject(self.pid, label=self.title)
            obj.addDataStream(u('RELS-EXT'))
            rels = obj['RELS-EXT']
            rels[NS.rdfs.hasModel].append(dict(
                type = u('uri'),
                value = u('info:fedora/'+pp('EPISODE'))
            ))
            rels.checksumType = u('DISABLED')
            rels.setContent()
            
        
    
class VideoForm(ModelForm):
    class Meta:
        model = Video
        