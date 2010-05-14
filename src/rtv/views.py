import rtv
from rtv.models import Video
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
#make sure to set <form enctype="multipart/form-data">
def upload(request):
    user = list(User.objects.all())[0]
    form = Video.get_new_form()
    context = {
        'rtv_version': rtv.get_version(),
        'title': "This is the rtv demo page",
        'form': form }
    if request.method == 'POST':
        form = Video.get_new_form(request.POST, request.FILES)
        context['form'] = form
        if form.is_valid():
            vals = form.cleaned_data
            vals['user'] = user
            Video.objects.create(**vals)
            context['title'] = "This is the rtv success page" 
            return render_to_response('rtv/success.html', context, RequestContext(request))
    return render_to_response('rtv/upload.html', context , RequestContext(request))
            
            
def demo(request):
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page"}, 
        RequestContext(request))
