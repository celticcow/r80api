#!/usr/bin/python -W ignore::DeprecationWarning

import requests
import json
import sys
import time
import getpass
import apifunctions



#### main()
if __name__ == "__main__":

    debug = 1

    ip_addr  = raw_input("Enter IP of MDS : ")
    ip_cma   = raw_input("Enter IP of CMA : ")
    user     = raw_input("Enter P1 User : ")
    password = getpass.getpass('Enter P1 Password :')

    sid = apifunctions.login(user, password, ip_addr, ip_cma)
    
    if(debug == 1):
        print("session id: " + sid)
    
    apifunctions.add_a_group(ip_addr, "oracle-ashburn-public-ranges", sid)

    ash = [
        "129.213.0.128/25",
        "129.213.2.128/25",
        "129.213.4.128/25",
        "130.35.16.0/22",
        "130.35.96.0/21",
        "130.35.144.0/22",
        "130.35.200.0/22",
        "134.70.24.0/21",
        "134.70.32.0/22",
        "138.1.48.0/21",
        "140.91.10.0/23",
        "140.91.12.0/22",
        "147.154.0.0/19"
    ]

    for net in ash:
        print("oracle-ashburn-" + net)

        parts = net.split('/')
        print("oracle-ashburn-" + parts[0])
        print(parts[0] + "--" + parts[1] + "+++" + apifunctions.calcDottedNetmask(int(parts[1])))
        apifunctions.add_a_network_with_group(ip_addr, "oracle-ashburn-" + parts[0], parts[0], apifunctions.calcDottedNetmask(int(parts[1])), "oracle-ashburn-public-ranges", sid)

        #print(apifunctions.calcDottedNetmask(24))

    """
    siteshield = [
        "104.71.131.0/24",
        "104.97.78.0/24",
        "184.24.98.0/24",
        "184.26.44.0/24",
        "184.28.127.0/24",
        "184.28.17.0/24",
        "184.51.151.0/24",
        "184.51.199.0/24",
        "184.84.239.0/24",
        "2.16.106.0/24",
        "2.18.240.0/24",
        "23.205.127.0/24",
        "23.211.118.0/24",
        "23.215.131.0/24",
        "23.216.10.0/24",
        "23.219.162.0/24",
        "23.219.163.0/24",
        "23.220.148.0/24",
        "23.34.58.0/24",
        "23.34.59.0/24",
        "23.42.158.0/24",
        "23.43.164.0/24",
        "23.62.239.0/24",
        "23.67.251.0/24",
        "23.79.240.0/24",
        "67.129.144.0/25",
        "72.246.150.0/24",
        "72.246.216.0/24",
        "96.7.55.0/24"
    ]
    
    for net in siteshield:
        print("siteShield-" + net)

        parts = net.split('/')
        print("siteShield-" + parts[0])
        print(parts[0] + "--" + parts[1] + "+++" + apifunctions.calcDottedNetmask(int(parts[1])))

        apifunctions.add_a_network(ip_addr, "siteShield-" + parts[0], parts[0], apifunctions.calcDottedNetmask(int(parts[1])), sid )

        #print(apifunctions.calcDottedNetmask(24))

    """
    #apifunctions.add_a_host(ip_addr, "test176", "146.18.2.99", sid)
    #apifunctions.add_a_network(ip_addr, "test176", "146.16.1.0", "255.255.255.0", sid)


    #apifunctions.add_a_group(ip_addr, "oracle-ashburn-public-ranges", sid)
    #apifunctions.add_a_host_with_group(ip_addr, "test176", "146.1.2.200", "group1", sid)
    #apifunctions.add_a_network_with_group(ip_addr, "gregnet4", "146.15.1.0", "255.255.255.0", "group1", sid)
    #apifunctions.add_a_network_with_group(ip_addr, "test176", "146.12.1.0", "255.255.255.0", "group1", sid)

    #apifunctions.add_a_range_with_group(ip_addr, "test76", "192.18.66.8", "192.18.66.77", "group3", sid)

    #apifunctions.add_group_to_group(ip_addr, "group2", "group1", sid)

    #if(apifunctions.name_exist(ip_addr, "test176", sid)):
     #   print("IT IS THERE")
    #else:
    #    print("can't find it")

    ### publish
    publish_result = apifunctions.api_call(ip_addr, "publish", {}, sid)
    print("publish result: " + json.dumps(publish_result))

    """
    when running over vpn seems fine
    when running network near logout does not always work only givin
    logout result: {"message": "Management server failed to execute command", "code": "generic_server_error"}
    """
    time.sleep(10)
    ### logout
    logout_result = apifunctions.api_call(ip_addr, "logout", {}, sid)
    print("logout result: " + json.dumps(logout_result))

    ### end of main () ###