import os
import rtv
from rtv.models import TranscodeJob, TranscodeJobForm
from rtv.fedora.datastream.forms import DublinCoreForm
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
            
def demo(request):
    objects = TranscodeJob.objects.filter(
                status=TranscodeJob.STATUS_PROCESSED)
    if objects.count() > 0: 
        vids = list(objects)[-1]
    else: vids = None
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page", 
            'vids': [vids]}, 
        RequestContext(request))

def upload(request):
    form = TranscodeJobForm()
    if request.method == 'POST':
        form = TranscodeJobForm(request.POST, request.FILES)
        if form.is_valid():
            vals = form.cleaned_data
            file = vals.pop('raw')
            vals['user'] = list(User.objects.all())[0]
            job = TranscodeJob.objects.create(**vals)
            basename, ext = os.path.splitext(os.path.basename(file.name))
            job.raw.save(basename+'_source'+ext, file, save=True)
            job.set_info()
            return redirect(info)
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
    """
    Shows a list of jobs that are in progress, or have been completed.  Links to
    individual jobs ingest view.
    """
    context = {'jobs': TranscodeJob.objects.all(), 'vids': TranscodeJob.objects.all(),
               'rtv_version': rtv.get_version(),
               'title': 'This is the rtv info page' }
    return render_to_response('rtv/info.html',
        context, 
        RequestContext(request))

def ingest(request, job_id):
    job = get_object_or_404(TranscodeJob, pk=int(job_id))
    job_data = {'title': job.title, 'creator': (job.user.get_full_name() 
                                                or job.user.username), 
                'type': 'video',
                'language': 'eng' }
    form = DublinCoreForm(job_data)
    
    if request.method == 'POST':
        form = DublinCoreForm(request.POST)
        
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv ingest page',
               'form': form }
    return render_to_response('rtv/ingest.html',
        context, 
        RequestContext(request))    