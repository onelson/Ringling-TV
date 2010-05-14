import rtv
from rtv.models import Video, UploadFileForm
from django.shortcuts import render_to_response
from django.template import RequestContext

#make sure to set <form enctype="multipart/form-data">
def upload_form(request):
    form = Video.get_new_form()
    if request.method == 'POST':
        form = Video.get_new_form(request.POST, request.FILES)
        if form.is_valid():
            vals = form.cleaned_data
            dict = Video.objects.create(**vals)
            UploadFileForm.handle_uploaded_file(request.FILES['file'])
            return render_to_response('rtv/success.html', mimetype="application/octet-stream")
        #no else
    else:
        form = Video.get_new_form()
        return render_to_response('rtv/upload.html', {'form': form},RequestContext(request))
            
            
def demo(request):
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page"}, 
        RequestContext(request))
