from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
import traceback
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
import os.path
import csv

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from models import epnm_info as epnm_info
from controllers.rest_calls import EPNM_Alarm as EPNM



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
# Display list of different locations for the site
@login_required(login_url = '/web/login/')
def index(request, loc = '', dev = '', location = ''):
    creds = epnm_info().get_info()
    epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
    location_list = epnm_obj.get_locations()
    return render(request, 'web_app/index.html', {'list':location_list})


# Redirect to index page
@login_required(login_url = '/web/login/')
def home(request):
    return render(request, 'web_app/home.html')


# Display list of different locations for the site
@login_required(login_url = '/web/login/')
def main(request):
    creds = epnm_info().get_info()
    epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
    location_list = epnm_obj.get_locations()
    return render(request, 'web_app/main.html', {'list':location_list})


# Display list of devices by IP address associated with a location
@login_required(login_url = '/web/login/')
def location_landing(request, loc):
    creds = epnm_info().get_info()
    epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
    dev_list = epnm_obj.get_group_devs(loc)
    show = True
    if len(dev_list) == 0: 
        dev_list.append('No Devices With Alarms to Report')
        show = False
    return render(request, 'web_app/location_landing.html', {
        'arg_in':loc, 
        'dev_list':dev_list,
        'show':show
    })


# Display list of alarms associated with a specific device
@login_required(login_url = '/web/login/')
def device_landing(request, dev):
    creds = epnm_info().get_info()
    epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
    alarm_info = epnm_obj.get_alarms(dev)
    download_url = device_writer(dev, alarm_info)
    base = os.path.dirname(os.path.abspath(__file__))
    output_file = base + "/out_file/alarm_report.csv"

    return render(request, 'web_app/device_landing.html', {
        'arg_in':dev, 
        'alarm_info':alarm_info,
        'download_link':output_file,
    })


# Display list of all devices associated with a location and all alarms associated with each device
@login_required(login_url = '/web/login/')
def location_dump(request, location):
    creds = epnm_info().get_info()
    epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
    alarm_list = epnm_obj.get_group_alarms(location)
    group_writer(alarm_list)
    base = os.path.dirname(os.path.abspath(__file__))
    output_file = base + '/out_files/alarm_report.csv'

    alarm_breakdown={}
    total_alarms = 0
    for item in alarm_list:
        for k in alarm_list[item]:
            for v in alarm_list[item][k]:
                if v=='Severity':
                    sev = alarm_list[item][k][v]
                    total_alarms += 1
                    if sev not in alarm_breakdown:
                        alarm_breakdown[sev]=1
                    else:
                        alarm_breakdown[sev]+=1

    return render(request, 'web_app/location_dump.html', {
        'arg_in':location,
        'alarm_list':alarm_list,
        'alarm_breakdown':alarm_breakdown,
        'total_alarms':total_alarms})


# Display login page
def login_view(request):
    return render(request, 'web_app/login.html')


# Authenticate entered user credentials
def auth_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)
    if user is not None:
        login(request, user)
        return redirect('/web/')
        # Redirect to a success page.
    else:
        return render(request, 'web_app/login.html', {'error_msg':'Invalid Login'})
        # Return an 'invalid login' error message.


# Send email containing alarm information for a location
def send_group_email_view(request):
    if request.GET.get('mybtn'):
        location = str(request.GET.get('mybtn'))
        creds = epnm_info().get_info()
        epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
        if epnm_obj.get_group_alarms(location) != {}:
            print "found"
            base = os.path.dirname(os.path.abspath(__file__))
            download_url = base + '/static/web_app/public/out_file/alarm_report.csv'
            subject = "EPNM Alarm Report for Devices in " + location
            epnm_obj.send_email("steveyee@cisco.com", "epnm84@gmail.com", subject, download_url)
        redirect_url = "/web/alarms/" + location
        return redirect(redirect_url)


# Send email containing alarm information for a specific device
def send_device_email_view(request):
    if request.GET.get('mybtn'):
        device = str(request.GET.get('mybtn'))
        print "Device is " + device
        creds = epnm_info().get_info()
        epnm_obj = EPNM(creds['host'], creds['user'], creds['password'])
        if epnm_obj.get_alarms(device) != {}:
            base = os.path.dirname(os.path.abspath(__file__))
            download_url = base + '/static/web_app/public/out_file/alarm_report.csv'
            subject = "EPNM Alarm Report for Device " + device
            epnm_obj.send_email("steveyee@cisco.com", "epnm84@gmail.com", subject, download_url)
        redirect_url = "/web/device/" + device
        return redirect(redirect_url)


# Create .csv file containing alarm information for a location
def group_writer(alarm_list):
    base = os.path.dirname(os.path.abspath(__file__))
    output_file = base + "/static/web_app/public/out_file/alarm_report.csv"

    with open(output_file, 'wb') as alarm_report:
        thisWriter = csv.writer(alarm_report)
        thisWriter.writerow(['Failure Source', 'Key', 'Acknowledgment Status', 'Time Stamp Created', 'Notes', 'Last Updated At', 'Description', 'Severity', ])
        for device_ip in alarm_list:
            for alarm in alarm_list[device_ip]:
                device_string = []
                device_string.append(device_ip)
                device_string.append(alarm)
                for key in alarm_list[device_ip][alarm]:                        
                    if key != "FailureSource":
                        device_string.append(alarm_list[device_ip][alarm][key])
                thisWriter.writerow(device_string)
    return output_file


# Create .csv file containing alarm information for a specific device
def device_writer(dev, alarm_info):
    base = os.path.dirname(os.path.abspath(__file__))
    output_file = base + "/static/web_app/public/out_file/alarm_report.csv"

    with open(output_file, 'wb') as alarm_report:
        thisWriter = csv.writer(alarm_report)
        thisWriter.writerow(['Failure Source', 'Key', 'Acknowledgment Status', 'Time Stamp Created', 'Notes', 'Last Updated At', 'Description', 'Severity'])
        for device_id in alarm_info:
            device_string = []
            device_string.append(alarm_info[device_id]['FailureSource'])
            device_string.append(str(device_id))
            for attribute in alarm_info[device_id]:
                if attribute != "FailureSource":
                    device_string.append(alarm_info[device_id][attribute])
            thisWriter.writerow(device_string)
    return output_file


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
