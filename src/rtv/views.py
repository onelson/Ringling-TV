import os
import rtv
from rtv.models import TranscodeJob, TranscodeJobForm
from rtv.fedora.models import Video
from rtv.fedora.datastream.forms import DublinCoreForm
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
            
def demo(request):
    processed = TranscodeJob.objects.filter(
                status=TranscodeJob.STATUS_PROCESSED)
    if processed.count() > 0:
        latest = list(processed.values_list('pk', flat=True))[-1]
    else: latest = False
    id = request.GET.get('id', latest)
    
    if id:
        vid = TranscodeJob.objects.get(pk=int(id))
    else: vid = None
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page", 
            'vid': vid,
            'links': processed.values_list('pk', 'title')}, 
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
            return redirect(reverse('rtv:queue'))
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
        if form.is_valid():
            Video.objects.create(user=job.user.username, raw=job.raw.url, 
                                 mp4=job.mp4.url, ogv=job.ogv.url, 
                                 thumbnail=job.thumbnail.url, 
                                 dc=form.cleaned_data)
            return redirect(reverse('rtv:queue'))
        
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv ingest page',
               'form': form }
    return render_to_response('rtv/ingest.html',
        context, 
        RequestContext(request))    