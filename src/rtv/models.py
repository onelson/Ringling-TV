"""
A collection of Django Models and related forms used in the fedora ingest 
process. 
"""

import json
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.files import File
import datetime, os
from rtv.transcoder import theora, h264, jpeg, TranscodeError
from rtv.settings import RTV_PID_NAMESPACE
from subprocess import Popen, PIPE
from rtv import settings
from rtv.storage import PermenantStorage

perm_storage = PermenantStorage()


def upload_dst(instance, filename):
    """
    This function determines the filesystem location of uploaded media, and the
    derived (transcoded) media.
    """
    path_components = [
        'uploads', 'processed', RTV_PID_NAMESPACE]
    path_components += [digit for digit in str(instance.pk)]
    path_components.append(filename)
    return r'%s' % os.path.join(*path_components)

class TranscodeJob(models.Model):
    """
    A transcode job is responsible for taking a 'source' video file and 
    generating derived formats and resized versions.
    """
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
    raw = models.FileField(upload_to=upload_dst, null=True, 
                           storage=perm_storage)
    
    ogv = models.FileField(upload_to=upload_dst, null=True, editable=False, 
                           storage=perm_storage)
    mp4 = models.FileField(upload_to=upload_dst, null=True, editable=False, 
                           storage=perm_storage)
    thumbnail = models.FileField(upload_to=upload_dst, null=True, 
                                 editable=False, storage=perm_storage)
    
    created = models.DateTimeField(auto_now_add=True)
    transcoded = models.DateTimeField(null=True, editable=False)
    
    info = models.TextField(editable=False, null=True)
        
    def transcode(self):
        self.status = self.STATUS_PROCESSING
        self.save()
        base = os.path.splitext(os.path.basename(self.raw.name))[0]
        try:
            jpg = jpeg(self.raw.path)
            self.thumbnail.save(base+'.jpg', File(open(jpg,'rb')))
            
            mp4 = h264(self.raw.path)
            self.mp4.save(base+'_h264.mp4', File(open(mp4,'rb')))
            
            ogv = theora(self.raw.path)
            self.ogv.save(base+'_theora.ogv', File(open(ogv,'rb')))
                
            self.status = self.STATUS_PROCESSED
            self.transcoded = datetime.datetime.now()
            self.save()
            # cleanup
            for file in [jpg, mp4, ogv]:
                os.remove(file)    
        except TranscodeError, err:
            self.STATUS_ERROR
            self.save()
            raise err
        
    def __unicode__(self):
        return unicode('<TranscodeJob: %s>' % (self.pk  or 'undefined')[0])
    def __str__(self): 
        return str(self.__unicode__())

    def set_info(self):
        cmd = '''%s --info "%s"''' % (settings.RTV_FFMPEG2THEORA, self.raw.path)
        self.info = Popen(cmd, stdout=PIPE, shell=True).communicate()[0]
        self.save()
        
    def get_info(self):
        return json.loads(self.info)
    @property
    def width(self):
        return int(self.get_info()['video'][0]['width'])
    @property
    def height(self):
        return int(self.get_info()['video'][0]['height'])
class TranscodeJobForm(ModelForm):
    class Meta:
        model = TranscodeJob