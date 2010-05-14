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
    title = models.CharField(max_length=100, editable=True)                                                 #video title
    video = models.FileField(upload_to='uploads', editable=True)                                  #the uploaded video
    video_flv = models.FileField(upload_to='processed_videos', editable=False, 
        null=True)                                  #the processed video
    uploaded_date = models.DateTimeField(auto_now_add=True, editable=False, 
        null=False)      #datetime the initial save() was called for this video
    process_start = models.DateTimeField(editable=False, null=True)                          #datetime status was set to 'processing'
    process_end = models.DateTimeField(editable=False, null=True)                            #datetime status was set to 'processed'
    status = models.IntegerField(editable=False, null=False)                        #status code
    #DC Metadata Fields
    DCtitle = models.CharField(max_length=100, editable=True, null=True)
    DCcreator = models.CharField(max_length=100, editable=False, null=False)
    DCsubject = models.CharField(max_length=100, editable=True, null=True)
    DCdescription = models.TextField(max_length=500, editable=True, null=True)
    DCpublisher = models.CharField(max_length=100, editable=True, null=True)
    DCcontributor = models.CharField(max_length=100, editable=True, null=True)
    DCdate = models.DateTimeField(editable=True, null=True)
    DCtype = models.CharField(max_length=50, editable=True, null=True)
    DCformat = models.CharField(max_length=25, editable=True, null=True)
    DCidentifier = models.CharField(max_length=50, editable=True, null=True)
    DCsource = models.CharField(max_length=50, editable=True, null=True)
    DClanguage = models.CharField(max_length=50, editable=True, null=True)
    DCrelation = models.CharField(max_length=50, editable=True, null=True)
    DCcoverage = models.CharField(max_length=50, editable=True, null=True)
    DCrights = models.TextField(max_length=800, editable=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, 
    default=STATUS_PENDING, editable=False)    #status code
    
    def get_new_form(*args, **kwargs):
        return NewVideoForm(*args, **kwargs)
    
class NewVideoForm(ModelForm):
    class Meta:
        model = Video
        fields = (
                  'user',
                  'title',
                  'video',
                  'video_flv',
                  'uploaded_date',
                  'process_start',
                  'process_end',
                  'status'
                  )
        
class FileUploadHandler(object):
    def new_file(self, content_type):
        self.content_type = 'video/x-msvideo', 'video/x-dv',  
        self.content_type = 'video/x-dv'
        self.content_type = 'video/vnd.mpegurl'
        self.content_type = 'video/x-m4v'
        self.content_type = 'video/quicktime'
        self.content_type = 'video/x-sgi-movie'
        self.content_type = 'video/mp4'
        self.content_type = 'video/mpeg'
    def recieve_data_chunk(self, raw_data, start):
        raise NotImplementedError()
    def file_complete(self, file_size):
        raise NotImplementedError()
    def upload_complete(self):
        pass
    
class UploadFileForm(models.FileField):
    def handle_uploaded_file(f, instance):
        instance.field.save('name_slug.ext', f, True)
        instance.save()
    def upload_file(self, request):
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                    UploadFileForm.handle_uploaded_file(request.FILES['file'])
                    return HttpResponseRedirect('/success/url/')
        else:
            form = UploadFileForm()
        return render_to_response('upload.html', {'form': form})
        