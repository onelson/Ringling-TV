import os
import rtv
from rtv.models import TranscodeJob, Video, TranscodeJobForm
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.files import File

            
def demo(request):
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page", 
            'vids': list(TranscodeJob.objects.filter(
                status=TranscodeJob.STATUS_PROCESSED))[:1]}, 
        RequestContext(request))

def upload(request):
    user = list(User.objects.all())[0]
    form = TranscodeJobForm()
    if request.method == 'POST':
        form = TranscodeJobForm(request.POST, request.FILES)
        if form.is_valid():
            vals = form.cleaned_data
            file = vals.pop('source')
            vals['user'] = list(User.objects.all())[0]
            video = TranscodeJob.objects.create(**vals)
            basename, ext = os.path.splitext(os.path.basename(file.name))
            video.source.save(basename+'_source'+ext, file, save=True)
            return redirect(success)
    context = {
        'rtv_version': rtv.get_version(),
        'title': "This is the rtv upload page",
        'form': form }
    return render_to_response('rtv/upload.html', context , RequestContext(request))

def success(request):
    return render_to_response('rtv/success.html',
        {'title': "Uploaded"},
        RequestContext(request))

def info(request):
    context = {'jobs': TranscodeJob.objects.all(), 'vids': Video.objects.all(),
               'rtv_version': rtv.get_version(),
               'title': 'This is the rtv info page' }
    return render_to_response('rtv/info.html',
        context, 
        RequestContext(request))