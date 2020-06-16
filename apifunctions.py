#!/usr/bin/python3 -W ignore::DeprecationWarning

import requests
import json
import sys

"""
Collection of Functions to do CheckPoint R80.xx api calls

Created : 08.12.2019 -- gdunlap
Last Update : 06.15.2020 -- gdunlap

version 1.1

todo

"""

"""
api_call function 
takes IP of mds / api command name / json payload / session ID as arg
"""
def api_call(ip_addr, command, json_payload, sid):
    url = "https://" + ip_addr + ":" + "/web_api/" + command
    if(sid == ""):
        request_headers = {"Content-Type" : "application/json"}
    else:
        request_headers = {"Content-Type": "application/json", "X-chkp-sid" : sid}
    
    r = requests.post(url,data=json.dumps(json_payload), headers=request_headers, verify=False)
    return r.json()

"""
Login function
payload to login to CMA
returns Session ID (SID)
"""
def login(user, password, mds, domain):
    payload = {"user" : user, "password" : password, "domain" : domain}
    response = api_call(mds, "login", payload, "")

    return response["sid"]

"""
convert a CIDR 24 to say 255.255.255.0
"""
def calcDottedNetmask(mask):
    bits = 0
    for i in range(32-mask,32): 
        bits |= (1 << i)
    return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8 , (bits & 0xff))

"""
add a group known by group to a group known by name
"""
def add_group_to_group(ip_addr, name, group, sid):
    print("temp -- in add_group_to_group")

    add_group_to_group_json = {
        "name" : group,
        "members" : {
            "add" : name
        }
    }
    out1 = api_call(ip_addr, "set-group", add_group_to_group_json, sid)
    print(json.dumps(out1))

"""
make sure a check point object with this name exist or not.
"""
def name_exist(ip_addr, name, sid):
    print("temp -- in name_exist")
    check_name = {"order" : [{"ASC" : "name"}], "in" : ["name", name] }
    chkname = api_call(ip_addr, "show-objects", check_name, sid)

    print(json.dumps(chkname))

    if(chkname['total'] == 0):
        return False
    else:
        return True
    
"""
see if group already exist as bool ... could do 
name_exist but this looks better
commented out lines for debug output
"""
def group_exist(ip_addr, name, sid):
    #print("temp -- in group_exist")
    check_name = {"order" : [{"ASC" : "name"}], "in" : ["name", name] }
    chkname = api_call(ip_addr, "show-objects", check_name, sid)
    
    #print("************* Group Exist JDump *************")
    #print(json.dumps(chkname))
    #print("************* ----------------- *************")

    if(chkname['total'] == 0):
        #nothing found with this name space
        #print("not a group or does not exist")
        return False
    """
     possible to get a group named "test99" and a host with prefix
     test99- that will both match on the show object so we can't just
     assume the index of [0] in the search for type will be 100% effective
    """
    for i in range(chkname['total']):
        if(chkname['objects'][i]['type'] == "group"):
            #print("This is a group yo")
            return True
    
    #default return case.  we had name matches but none were groups
    #print("not a group or does not exist")
    return False

"""
add a new group
"""
def add_a_group(ip_addr, name, sid):
    print("temp -- in add_a_group")
    check_group_obj = {"type" : "group", "order" : [{"ASC" : "name"}], "in" : ["name", name] }
    chkgrp = api_call(ip_addr, "show-objects", check_group_obj, sid)
    print(json.dumps(chkgrp))

    if(chkgrp['total'] == 0):
        #we can add a group
        if(name_exist(ip_addr, name, sid) == False):
            group_to_add = {"name" : name, "color" : "light green"}
            out1 = api_call(ip_addr, "add-group", group_to_add, sid)
            print(json.dumps(out1))
        else:
            print("object with that name already exist")
    else:
        #group already exist ... do nothing for now
        print("group already exist")

"""
add a host
"""
def add_a_host(ip_addr, name, ip, sid):
    print("temp -- in add_a_host<br>")
    check_host_obj = {"type" : "host", "filter" : ip, "ip-only" : "true"}
    chkhst = api_call(ip_addr, "show-objects", check_host_obj, sid)

    if(chkhst['total'] == 0):
        #need new host
        if(name_exist(ip_addr, name, sid) == False):
            host_to_add = {"name" : name, "ip-address" : ip, "color" : "light green"}
            out1 = api_call(ip_addr, "add-host", host_to_add, sid)
            print(json.dumps(out1))
        else:
            print("object with that name already exist")
    else:
        # host exist ... 
        print("host already exist")

"""
add a network
"""
def add_a_network(ip_addr, name, network, netmask, sid):
    ## check to see if network exist already
    check_network_obj = {"type" : "network", "filter" : network, "ip-only" : "true", "limit" : "50"}
    chknet = api_call(ip_addr, "show-objects", check_network_obj, sid)

    """
    if filter shows 0 total don't go any further and add
    if filter returns some results check exact netmasks and make sure 
    """
    if(chknet['total'] == 0):
        #need to add network nothing close ... just do it
        if(name_exist(ip_addr, name, sid) == False):
            net_to_add = {"name": name, "subnet4" : network, "subnet-mask" : netmask}
            netadd = api_call(ip_addr, "add-network", net_to_add, sid)

            print(json.dumps(netadd))
        else:
            print("object with that name already exist")  
    else:
        found = 0
        print(json.dumps(chknet))

        #search possible results
        for i in range(chknet['total']):
            print(chknet['objects'][i]['name'])
            print(chknet['objects'][i]['subnet4'])
            print(chknet['objects'][i]['subnet-mask'])
            print("------------------------------")
            if((chknet['objects'][i]['subnet4'] == network) and (chknet['objects'][i]['subnet-mask'] == netmask)):
                #good job ... we found it.
                print("*****************************")
                print("match at  ")
                found = 1
                print(chknet['objects'][i]['name'])
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        if(found == 0):
            # we found some stuff that was close but not exact match so add this thing
            if(name_exist(ip_addr, name, sid) == False):
                net_to_add = {"name": name, "subnet4" : network, "subnet-mask" : netmask}
                netadd = api_call(ip_addr, "add-network", net_to_add, sid)

                print(json.dumps(netadd))
            else:
                print("object with that name already exist")

"""
add a network range
"""
def add_a_range(ip_addr, name, startip, endip, sid):
    print("temp -- in add_a_range<br>")
    check_range_obj = {"type" : "address-range", "filter" : startip, "ip-only" : "true", "limit" : "50"}
    chkrng = api_call(ip_addr, "show-objects", check_range_obj, sid)

    if(chkrng['total'] == 0):
        # go ahead and add range ... unlikly this will ever hit due ot all_internet object
        if(name_exist(ip_addr, name, sid) == False):
            range_to_add = {"name" : name, "ipv4-address-first" : startip, "ipv4-address-last" : endip}
            rangeadd = api_call(ip_addr, "add-address-range", range_to_add, sid)
        else:
            print("object with that name already exist")
    else:
        found = 0
        print(json.dumps(chkrng))

        for i in range(chkrng['total']):
            print("-----------------------")
            print(chkrng['objects'][i]['name'])
            print(chkrng['objects'][i]['ipv4-address-first'])
            print(chkrng['objects'][i]['ipv4-address-last'])

            if((chkrng['objects'][i]['ipv4-address-first'] == startip) and (chkrng['objects'][i]['ipv4-address-last'] == endip)):
                print("**************************")
                print(" match at  ")
                found = 1
                print(chkrng['objects'][i]['name'])
        
        if(found == 0):
            ## we found some stuff but no exact match
            if(name_exist(ip_addr, name, sid) == False):
                range_to_add = {"name" : name, "ipv4-address-first" : startip, "ipv4-address-last" : endip}
                rangeadd = api_call(ip_addr, "add-address-range", range_to_add, sid)

                print(json.dumps(rangeadd))
            else:
                print("object with that name already exist")

"""
add a host object and add it to a group
"""
def add_a_host_with_group(ip_addr, name, ip, group, sid):
    print("temp -- in add_a_host<br>")
    check_host_obj = {"type" : "host", "filter" : ip, "ip-only" : "true"}
    chkhst = api_call(ip_addr, "show-objects", check_host_obj, sid)

    if(chkhst['total'] == 0):
        #need new host
        if(name_exist(ip_addr, name, sid) == False):
            host_to_add = {"name" : name, "ip-address" : ip, "groups" : group, "color" : "light green"}
            out1 = api_call(ip_addr, "add-host", host_to_add, sid)
            print(json.dumps(out1))
        else:
            print("object with that name already exist")
    else:
        # host exist ... 
        print("host already exist")
        existing_host_name = chkhst['objects'][0]['name'] # name of existing host
        add_host_to_group_json = {
            "name" : group,
            "members" : {
                "add" : existing_host_name
            }
        }
        out1 = api_call(ip_addr, "set-group", add_host_to_group_json, sid)
        print(json.dumps(out1))

"""
add a network object and add it to a group
"""
def add_a_network_with_group(ip_addr, name, network, netmask, group, sid):
    ## check to see if network exist already
    check_network_obj = {"type" : "network", "filter" : network, "ip-only" : "true", "limit" : "50"}
    chknet = api_call(ip_addr, "show-objects", check_network_obj, sid)

    """
    if filter shows 0 total don't go any further and add
    if filter returns some results check exact netmasks and make sure 
    """
    if(chknet['total'] == 0):
        #need to add network nothing close ... just do it
        if(name_exist(ip_addr, name, sid) == False):
            net_to_add = {"name": name, "subnet4" : network, "subnet-mask" : netmask, "groups" : group}
            netadd = api_call(ip_addr, "add-network", net_to_add, sid)

            print(json.dumps(netadd)) 
        else:
            print("object with that name already exist")       
    else:
        found = 0
        print(json.dumps(chknet))

        #search possible results
        for i in range(chknet['total']):
            print(chknet['objects'][i]['name'])
            print(chknet['objects'][i]['subnet4'])
            print(chknet['objects'][i]['subnet-mask'])
            print("------------------------------")
            if((chknet['objects'][i]['subnet4'] == network) and (chknet['objects'][i]['subnet-mask'] == netmask)):
                #good job ... we found it.
                print("*****************************")
                print("match at  ")
                found = 1
                print(chknet['objects'][i]['name'])
                add_host_to_group_json = {
                    "name" : group,
                    "members" : {
                        "add" : chknet['objects'][i]['name']
                    }
                }
                out1 = api_call(ip_addr, "set-group", add_host_to_group_json, sid)
                print(json.dumps(out1))
            
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        if(found == 0):
            # we found some stuff that was close but not exact match so add this thing
            if(name_exist(ip_addr, name, sid) == False):
                net_to_add = {"name": name, "subnet4" : network, "subnet-mask" : netmask, "groups" : group}
                netadd = api_call(ip_addr, "add-network", net_to_add, sid)

                print(json.dumps(netadd))
            else:
                print("object with that name already exist")

"""
add a network range with group
"""
def add_a_range_with_group(ip_addr, name, startip, endip, group, sid):
    print("temp -- in add_a_range<br>")
    check_range_obj = {"type" : "address-range", "filter" : startip, "ip-only" : "true", "limit" : "50"}
    chkrng = api_call(ip_addr, "show-objects", check_range_obj, sid)

    if(chkrng['total'] == 0):
        # go ahead and add range ... unlikly this will ever hit due ot all_internet object
        if(name_exist(ip_addr, name, sid) == False):
            range_to_add = {"name" : name, "ipv4-address-first" : startip, "ipv4-address-last" : endip, "groups" : group}
            rangeadd = api_call(ip_addr, "add-address-range", range_to_add, sid)
        else:
            print("object with that name already exist")
    else:
        found = 0
        print(json.dumps(chkrng))

        for i in range(chkrng['total']):
            print("-----------------------")
            print(chkrng['objects'][i]['name'])
            print(chkrng['objects'][i]['ipv4-address-first'])
            print(chkrng['objects'][i]['ipv4-address-last'])

            if((chkrng['objects'][i]['ipv4-address-first'] == startip) and (chkrng['objects'][i]['ipv4-address-last'] == endip)):
                print("**************************")
                print(" match at  ")
                found = 1
                print(chkrng['objects'][i]['name'])
                add_range_to_group_json = {
                    "name" : group,
                    "members" : {
                        "add" : chkrng['objects'][i]['name']
                    }
                }
                out1 = api_call(ip_addr, "set-group", add_range_to_group_json, sid)
                print(json.dumps(out1))
        
        if(found == 0):
            ## we found some stuff but no exact match
            if(name_exist(ip_addr, name, sid) == False):
                range_to_add = {"name" : name, "ipv4-address-first" : startip, "ipv4-address-last" : endip, "groups" : group}
                rangeadd = api_call(ip_addr, "add-address-range", range_to_add, sid)

                print(json.dumps(rangeadd))
            else:
                print("object with taht name already exist")


"""
add a tcp service
"""
def add_a_tcp_port(ip_addr, port, sid):
    ## check to see if the port exist already
    check_service_obj = {"type": "service-tcp", "filter" : port, "limit" : "50"}
    chkservice = api_call(ip_addr, "show-objects", check_service_obj, sid)

    #print(json.dumps(chkservice))
    if(chkservice['total'] == 0):
        #need to add a port .. no match or near match
        name = "tcp-" + str(port)
        if(name_exist(ip_addr, name, sid) == False):
            ## add the port
            port_to_add = {"name" : name, "port" : port}
            portadd = api_call(ip_addr, "add-service-tcp", port_to_add, sid)
        else:
            print("object with name " + name + " exist already but does not match port number")

    else:
        #may be a port may not (80 vs 8080)
        found = 0
        for i in range(chkservice['total']):
            #print(chkservice['objects'][i]['port'])
            if(chkservice['objects'][i]['port'] == port):
                #found match
                print("Port Already Found : " + chkservice['objects'][i]['name'])
                found = 1
        if(found == 0):
            #add port
            name = "tcp-" + str(port)
            if(name_exist(ip_addr, name, sid) == False):
                ## add the port
                port_to_add = {"name" : name, "port" : port}
                portadd = api_call(ip_addr, "add-service-tcp", port_to_add, sid)
            else:
                print("object with name " + name + " exist already but does not match port number")


"""
add a udp service
"""
def add_a_udp_port(ip_addr, port, sid):
    ## check to see if the port exist already
    check_service_obj = {"type": "service-udp", "filter" : port, "limit" : "50"}
    chkservice = api_call(ip_addr, "show-objects", check_service_obj, sid)

    #print(json.dumps(chkservice))
    if(chkservice['total'] == 0):
        #need to add a port .. no match or near match
        name = "udp-" + str(port)
        if(name_exist(ip_addr, name, sid) == False):
            ## add the port
            port_to_add = {"name" : name, "port" : port}
            portadd = api_call(ip_addr, "add-service-udp", port_to_add, sid)
        else:
            print("object with name " + name + " exist already but does not match port number")

    else:
        #may be a port may not (80 vs 8080)
        found = 0
        for i in range(chkservice['total']):
            #print(chkservice['objects'][i]['port'])
            if(chkservice['objects'][i]['port'] == port):
                #found match
                print("Port Already Found : " + chkservice['objects'][i]['name'])
                found = 1
        if(found == 0):
            #add port
            name = "udp-" + str(port)
            if(name_exist(ip_addr, name, sid) == False):
                ## add the port
                port_to_add = {"name" : name, "port" : port}
                portadd = api_call(ip_addr, "add-service-udp", port_to_add, sid)
            else:
                print("object with name " + name + " exist already but does not match port number")

"""
Check to see if an object is in a locked state or not
"""
def object_is_locked(ip_addr, name, sid):
    debug = 0

    if(debug == 1):
        print("in object_is_locked()")

    check_object = {
        "order" : [{"ASC" : "name"}], 
        "in" : ["name", name],
        "details-level" : "full"      
    }
    
    obj_result = api_call(ip_addr, "show-objects", check_object, sid)

    if(debug == 1):
        print(json.dumps(obj_result))
        print("\n\n")
    
    if(obj_result['objects'][0]['meta-info']['lock'] == "unlocked"):
        # object is unlocked so it's not false to is_locked
        return False
    else:
        # default to locked
        return True


#end of file