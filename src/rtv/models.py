from django.db import models
from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect


class Video(models.Model):
    user = models.ForeignKey(editable=False, null=False)                                     #user doing the upload (request.user)
    title = models.CharField(max_legnth=100, editable=True)                                  #video title
    video = models.FileField(upload_to=None, editable=True)                                  #the uploaded video
    video_flv = models.FileField(editable=False, null=True)                                  #the processed video
    uploaded_date = models.DateTimeField(auto_add_now=True, editable=False, null=False)      #datetime the initial save() was called for this video
    process_start = models.DateTimeField(editable=False, null=True)                          #datetime status was set to 'processing'
    process_end = models.DateTimeField(editable=False, null=True)                            #datetime status was set to 'processed'
    status = models.IntegerField(editable=False, null=False)                                 #status code
    
    
class FileUploadHandler(object):
    def new_file(self, content_type):
        self.content_type = 'video/x-msvideo' 
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
    
    
class DCMetadata(models.Model):
    #DC Metadata Fields
    title = models.CharField(max_length=100, editable=True, null=True)
    creator = models.ForeignKey(editable=False, null=False)
    subject = models.CharField(max_length=100, editable=True, null=True)
    description = models.TextField(max_length=250, editable=True, null=True)
    publisher = models.CharField(max_length=100, editable=True, null=True)
    contributor = models.CharField(max_length=100, editable=True, null=True)
    date = models.DateTimeField(editable=True, null=True)
    type = models.CharField(max_length=50, editable=True, null=True)
    format = models.CharField(max_length=25, editable=True, null=True)
    identifier = models.CharField(max_length=50, editable=True, null=True)
    source = models.CharField(max_length=50, editable=True, null=True)
    language = models.CharField(max_length=50, editable=True, null=True)
    relation = models.CharField(max_length=50, editable=True, null=True)
    coverage = models.CharField(max_length=50, editable=True, null=True)
    rights = models.CharField(max_length=100, editable=True, null=True)
    
class UploadFileForm(forms.Form):
    def upload_file(self, request):
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                    #handle_uploaded_file(request.FILES['file'])
                    return HttpResponseRedirect('/success/url/')
        else:
            form = UploadFileForm()
        return render_to_response('upload.html', {'form': form})
        