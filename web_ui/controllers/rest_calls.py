#!/usr/bin/env python
__author__ = "Michael Castellana and Steven Yee"
__email__ = "micastel@cisco.com and steveyee@cisco.com"
__status__ = "Development"

#import necessary libraries
import base64, getpass, requests, json, sys, smtplib, csv, os
from .. import opensesame
from email.mime.multipart import MIMEMultipart
from email.message import Message
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

class EPNM_Alarm:

    requests.packages.urllib3.disable_warnings()

    # Set default values for authorization and host site location
    def __init__(self,host, user, pwd, verify=False):
        self.authorization = "Basic " + base64.b64encode(user + ":" + pwd)
        self.host = host


    # Create default headers needed for EPNM Rest API 
    def get_headers(self, auth, content_type = "application", cache_control = "no-cache"):
        headers={
            'content-type': content_type,
            'authorization': self.authorization,
            'cache-control': cache_control,
        }
        return headers


    # Send GET request to EPNM API
    def get_response(self, url, headers, requestType = "GET", verify = False):
        return requests.request(requestType, url, headers=headers, verify = verify).json()


    # Formulate GET request for individual devices and send it by calling get_response()
    def make_get_req(self, auth, host, ext, filters = ""):
        headers = self.get_headers(auth)
        url = "https://"+host+"/webacs/api/v1/data/"+ext+".json?"+filters
        return self.get_response(url, headers, requestType = "GET", verify = False)


    # Formulate GET request for location groups and send it by calling get_response()
    def make_group_get_req(self, auth, host, ext, filters = ""):
        headers = self.get_headers(auth)
        url = "https://"+host+"/webacs/api/v1/op/groups/"+ext+".json?"+filters
        return self.get_response(url, headers, requestType = "GET", verify = False)


    # Parse through EPNM response for device IDs
    def get_device_ID_list(self, response):
        id_list = []
        for item in response:
            id_list.append(str(item['$']))
        return id_list


    # Send email
    def send_email(self, destination_address, source_address, subject, attachment_url):
        email_message = MIMEMultipart()
        email_message['subject'] = subject
        email_message['From'] = source_address
        email_message['To'] = destination_address
        message_body = MIMEText("Attached is an alarm report.")
        email_message.attach(message_body)
        with open(attachment_url) as file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment',
                              filename=os.path.basename(attachment_url))
        email_message.attach(attachment)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(source_address, opensesame.email_password)
        server.sendmail(source_address, destination_address, email_message.as_string())
        server.quit()


    # Return alarm information for all devices in a group
    def get_group_alarms(self, group):
        group_alarms = {}
        group_device_list = self.get_group_devs(group)
        for device in group_device_list:
            device_alarms = self.get_alarms(device)
            group_alarms[device] = device_alarms
        return group_alarms


    # Return list of device IDs (IP addresses) in a specific group that have valid alarms
    def get_group_devs(self, group):
        id_list = []
        extension = 'Devices'
        filters = ".full=true&.group="+group
        response = self.make_get_req(self.authorization, self.host, extension, filters)
        response = response['queryResponse']['entity']
        for dev in response:
            bulk = dev['devicesDTO']
            if bulk['criticalAlarms']!=0 or bulk['informationAlarms']!=0 or bulk['majorAlarms']!=0 or bulk['minorAlarms']!=0 or bulk['warningAlarms']!=0:
                id_list.append(bulk['ipAddress'])
        return id_list


    # Retrieve information on all alarms attached to a specific device identified by IP address
    def get_alarms(self, dev):
        extension = 'Alarms'
        filters = '.full=true'
        no_cleared_filters = ".full=true&source=\""+dev+"\"&severity=ne(\"CLEARED\")"
        response = self.make_get_req(self.authorization, self.host, extension, no_cleared_filters)['queryResponse']['entity']
        r_dict={}
        for item in response:
            info={}
            info['Severity'] = item['alarmsDTO']['severity']
            info['Condition'] = item['alarmsDTO']['condition']['value']
            info['Description'] = item['alarmsDTO']['message']
            info['TimeStamp'] = item['alarmsDTO']['timeStamp']
            info['FailureSource'] = item['alarmsDTO']['source']
            info['LastUpdatedAt'] = item['alarmsDTO']['lastUpdatedAt']
            info['AcknowledgmentStatus'] = item['alarmsDTO']['acknowledgementStatus']
            if 'annotations' in item['alarmsDTO']:
                info['Notes'] = item['alarmsDTO']['annotations']
            else:
                info['Notes'] = "No Notes"
            r_dict[item['alarmsDTO']['@id']] = info
        return r_dict


    # Return list of locations defined for the site
    def get_locations(self):
        site_list = []
        extension = 'sites'
        filters = '.full=true'
        response = self.make_group_get_req(self.authorization, self.host, extension, filters)['mgmtResponse']['siteOpDTO']
        for item in response:
            if item['deviceCount'] != 0:
                site_list.append(item['name'][item['name'].rfind('/')+1:])

        return site_list
