from django.shortcuts import render_to_response
from django.template import RequestContext
import rtv
def demo(request):
    return render_to_response('rtv/demo.html',
        {'rtv_version': rtv.get_version(),'title': "This is the rtv demo page"}, 
        RequestContext(request))