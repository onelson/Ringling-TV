import os, datetime
import rtv
from rtv.models import TranscodeJob, TranscodeJobForm
from rtv.fedora.models import Video, ObjectNotFoundError
from rtv.fedora.datastream.forms import DublinCoreForm
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
            
def demo(request):
    all = Video.objects.all()
    if all:
        latest = all[-1]
    else:
        latest = None
        
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page", 
            'vid': latest,
            'all': all}, 
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

def video_ingest(request, job_id):
    job = get_object_or_404(TranscodeJob, pk=int(job_id))
    job_data = {'title': job.title, 'creator': (job.user.get_full_name() 
                                                or job.user.username), 
                'type': 'video',
                'language': 'eng',
                'date': datetime.date.today() }
    form = DublinCoreForm(job_data)
    
    if request.method == 'POST':
        form = DublinCoreForm(request.POST)
        if form.is_valid():
            Video.objects.create(user=job.user.username, raw=job.raw.url, 
                                 raw_info=job.info, mp4=job.mp4.url, 
                                 ogv=job.ogv.url, thumbnail=job.thumbnail.url, 
                                 dc=form.cleaned_data)
            job.delete()
            return redirect(reverse('rtv:queue'))
        
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv ingest page',
               'form': form }
    return render_to_response('rtv/video_ingest.html',
        context, 
        RequestContext(request))

def video_list(request):
    videos = Video.objects.all()
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv video list page',
               'object_list': videos }
    return render_to_response('rtv/video_list.html',
        context, 
        RequestContext(request))
    
def video_detail(request, pid):
    try: 
        video = Video.objects.get(pid=pid)
    except ObjectNotFoundError:
        raise Http404
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv video detail page',
               'object': video }
    return render_to_response('rtv/video_detail.html',
        context, 
        RequestContext(request))

def video_update(request, pid):
    video = Video.objects.get(pid=pid)
    form = DublinCoreForm(video.dc_as_dict())
    
    if request.method == 'POST':
        form = DublinCoreForm(request.POST)
        if form.is_valid():
            video.dict_to_dc(form.cleaned_data)
            return redirect(reverse('rtv:video_list'))
    context = {'rtv_version': rtv.get_version(),
               'title': 'This is the rtv ingest page',
               'form': form }
    return render_to_response('rtv/video_update.html',
        context, 
        RequestContext(request))

def video_state(request, pid, state):
    """
    Toggles between 'A' and 'D' states
    """ 
    vid = Video.objects.get(pid=pid)
    vid.__fcobj__.state = unicode(state)
    return redirect(reverse('rtv:video_list'))

def video_delete(request, pid):
    """
    Displays a confirmation page, with a simple delete form.
    This will purge the object from the repo: final death, no regeneration!
    """ 
    vid = Video.objects.get(pid=pid)
    vid.delete()
    return redirect(reverse('rtv:video_list'))