from django.db import models
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.forms import ModelForm

class Video(models.Model):
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
    user = models.ForeignKey(User, editable=False)                                           #user doing the upload (request.user)
    title = models.CharField(max_length=100, editable=True)                                  #video title
    video = models.FileField(upload_to='uploads', editable=True)                             #the uploaded video
    video_flv = models.FileField(upload_to='processed_videos', editable=False, null=True)    #the processed video
    uploaded_date = models.DateTimeField(auto_now_add=True, editable=False, null=False)      #datetime the initial save() was called for this video
    title = models.CharField(max_length=100)                                                 #video title
    video = models.FileField(upload_to='uploads')                                  #the uploaded video
    video_flv = models.FileField(upload_to='processed_videos', editable=False, 
        null=True)                                  #the processed video
    uploaded_date = models.DateTimeField(auto_now_add=True, editable=False, 
        null=False)      #datetime the initial save() was called for this video
    process_start = models.DateTimeField(editable=False, null=True)                          #datetime status was set to 'processing'
    process_end = models.DateTimeField(editable=False, null=True)                            #datetime status was set to 'processed'
    status = models.SmallIntegerField(choices=STATUS_CHOICES, 
    default=STATUS_PENDING, editable=False)    #status code
    #DC Metadata Fields
    DCsubject = models.CharField(max_length=100, blank=True, null=True)
    DCdescription = models.TextField(max_length=500, blank=True, null=True)
    DCpublisher = models.CharField(max_length=100, blank=True, null=True)
    DCcontributor = models.CharField(max_length=100, blank=True, null=True)
    DCdate = models.DateTimeField(blank=True, null=True)
    DCtype = models.CharField(max_length=50, blank=True, null=True)
    DCformat = models.CharField(max_length=25, blank=True, null=True)
    DCidentifier = models.CharField(max_length=50, blank=True, null=True)
    DCsource = models.CharField(max_length=50, blank=True, null=True)
    DClanguage = models.CharField(max_length=50, blank=True, null=True)
    DCrelation = models.CharField(max_length=50, blank=True, null=True)
    DCcoverage = models.CharField(max_length=50, blank=True, null=True)
    DCrights = models.TextField(max_length=800, blank=True, null=True)
    
    
    @staticmethod
    def get_new_form(*args, **kwargs):
        return NewVideoForm(*args, **kwargs)
    
class NewVideoForm(ModelForm):
    class Meta:
        model = Video