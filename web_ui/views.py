from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import traceback
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer



# ====================>>>>>>>> Utils <<<<<<<<====================
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# ====================>>>>>>>> Templates <<<<<<<<====================

def index(request):
    return render(request, 'web_app/index.html')


def home(request):
    return render(request, 'web_app/home.html')


# ====================>>>>>>>> APIs <<<<<<<<====================
@csrf_exempt
def api_example(request):
    """
    Example of API
    :param request:
    :return:
    """
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            print(payload)
            return JSONResponse({"response": "it Works"})
        except Exception as e:
            print(traceback.print_exc())
            # return the error to web client
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
    else:
        return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
