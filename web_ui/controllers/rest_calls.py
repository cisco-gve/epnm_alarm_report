#!/usr/bin/env python
__author__ = "Michael Castellana and Steven Yee"
__email__ = "micastel@cisco.com and steveyee@cisco.com"
__status__ = "Development"

#import necessary libraries
import base64, getpass, requests, json, sys

class EPNM_Alarm:

    requests.packages.urllib3.disable_warnings()

    def __init__(self,host, user, pwd, verify=False):
        self.authorization = "Basic " + base64.b64encode(user + ":" + pwd)
        self.host = host

    def get_headers(self, auth, content_type = "application", cache_control = "no-cache"):
        headers={
            'content-type': content_type,
            'authorization': self.authorization,
            'cache-control': cache_control,
        }
        return headers

    def get_response(self, url, headers, requestType = "GET", verify = False):
        return requests.request(requestType, url, headers=headers, verify = verify).json()

    def make_get_req(self, auth, host, ext, filters = ""):
        headers = self.get_headers(auth)
        url = "https://"+host+"/webacs/api/v1/data/"+ext+".json?"+filters
        return self.get_response(url, headers, requestType = "GET", verify = False)

    def make_group_get_req(self, auth, host, ext, filters = ""):
        headers = self.get_headers(auth)
        url = "https://"+host+"/webacs/api/v1/op/groups/"+ext+".json?"+filters
        return self.get_response(url, headers, requestType = "GET", verify = False)

    def get_device_ID_list(self, response):
        id_list = []
        for item in response:
            id_list.append(str(item['$']))
        return id_list




    def get_group_devs(self, group):
        id_list = []
        #print group
        extension = 'Devices'
        filters = ".full=true&.group="+group
        response = self.make_get_req(self.authorization, self.host, extension, filters)
        response = response['queryResponse']['entity']
        for dev in response:
            bulk = dev['devicesDTO']
            if bulk['criticalAlarms']!=0 or bulk['informationAlarms']!=0 or bulk['majorAlarms']!=0 or bulk['minorAlarms']!=0 or bulk['warningAlarms']!=0:
                id_list.append(bulk['ipAddress'])
        #print json.dumps(response, indent=2)
        return id_list

    def get_groupings(self):
        group_list = []
        extension = 'deviceGroups'
        filters = '.full=true'
        response = self.make_get_req(self.authorization, self.host, extension)['mgmtResponse']['grpDTO']
        for item in response:
            group_list.append(item['groupName'])
        return group_list

    def get_alarms(self, dev):
        extension = 'Alarms'
        filters = '.full=true'
        no_cleared_filters = ".full=true&source=\""+dev+"\"&severity=ne(\"CLEARED\")"
        #***-->group filtering--> .group="GROUP"
        response = self.make_get_req(self.authorization, self.host, extension, no_cleared_filters)#['queryResponse']['entity']
        #print len(response)

        print json.dumps(response, indent=2)


    # ********** FILTERING NOT WORKING YET --GETTIN 403 DENIAL
    def get_group_alarms(self, group):
        extension = 'Alarms'
        filters = '.full=true'
        no_cleared_filters = ".full=true&severity=ne(\"CLEARED\")"
        group_filter = ".group="+group

        #response = make_get_req(auth, host, extension, no_cleared_filters)['queryResponse']['entity']
        response = self.make_get_req(self.authorization, self.host, extension, group_filter)
        print response
        print json.dumps(response, indent=2)
    # **************** FIX FILTERING

    def get_alarm_summary(self):
        """ Queries all registered Guests"""
        extension = 'alarmSummary'
        response = self.make_group_get_req(auth, host, extension)
        print json.dumps(response, indent=2)

    def get_locations(self):
        """ Queries all registered Guests"""
        site_list = []
        extension = 'sites'
        filters = '.full=true'
        response = self.make_group_get_req(self.authorization, self.host, extension, filters)['mgmtResponse']['siteOpDTO']
        for item in response:
            if item['deviceCount'] != 0:
                #print item['name'] + ' - '+ str(item['deviceCount'])
                site_list.append('/'+item['name'])

        return site_list
        #print json.dumps(response, indent=2)




    if __name__ == '__main__':
        #Disable warnings since we are not verifying SSL
        requests.packages.urllib3.disable_warnings()
        host_addr = 'tme-epnm'
        # user = raw_input("User: ")
        # pwd = getpass.getpass("Password: ")

        #use above for taking in arguments- i got lazy so i didnt feel like typing it each time
        #i just took the commands at run time
        user = sys.argv[1]
        pwd = sys.argv[2]
        auth = base64.b64encode(user + ":" + pwd)

        #test case
        # group_name = "/Location/All Locations/US"

        #uncomment below for single test case
        #TESTING WITH DEVICE ID 6051045 -- 172.23.193.142
        get_alarms(auth, host_addr, "172.23.193.142")




        sites = get_locations(auth, host_addr)
        site_mappings = {}


        for loc in sites:
            dev_list = get_group_devs(auth, host_addr, loc)
            site_mappings[loc] = dev_list
        
        #site pairings
        for k in site_mappings:
            v = site_mappings[k]
            print (k,v)

        #alarm readout
        # for site in site_mappings:
        #     print "+++++++ LOCATION - "+str(site)+" ++++++++"
        #     dev_list = site_mappings[site]
        #     for dev in dev_list:
        #         print "--- Device "+str(dev)+" ---"
        #         get_alarms(auth, host_addr, dev)
        #         print '\n------------------------------\n\n'

    # https://tme-epnm/webacs/api/v1/data/Alarms/.json?.full=true&source="172.23.193.142"&severity=ne("CLEARED")
       
        #get_group_alarms(auth, host_addr, test_site) --? #GET 403 DENIAL

        #for dev in site_mappings[test_site]:




        """ THE FOLLOWING METHODS ARE TESTING PURPOSES FOR TESTING THE EFFECTIVENSS OF INDIVIDUAL CALLS"""
        """ EVERYTHING BELOW SHOULD NOT BE CONSIDERED FOR PRODUCTION AND ONLY THE ABOVE SHOULD BE EDITED FOR USE"""
        # print '======    Alarms    ======='
        # get_alarms(auth, host_addr)
        # print '\n\n'

        # ->Filtering not working properly
        # print '======    Group-Alarm    ======='
        # get_group_alarms(auth, host_addr, group_name)
        # print '\n\n'    

        # print '======    GROUPS    ======='
        # get_groupings(auth, host_addr)
        # print '\n\n'

        # print '======    GROUP Devices    ======='
        # get_group_devs(auth, host_addr, group_name)
        # print '\n\n'

        # print '======    TEST    ======='
        # export_dev_call(auth, host_addr)
        # print '\n\n'

        # print '======    LOCATIONS    ======='
        # get_locations(auth, host_addr)
        # print '\n\n'

        # print '======    Summary    ======='
        # get_alarm_summary(auth, host_addr)
        # print '\n\n'





