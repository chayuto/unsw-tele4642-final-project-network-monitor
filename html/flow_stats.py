#!/usr/bin/python
# Copyright 2015 Chayut, Thanchanok, Vincent, Michale
# Q2hheXV0T3JhcGlucGF0aXBhdA==
#

"""
"""

# standard includes
from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
import csv
import os
from datetime import datetime
import pandas as pd
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()
flowList = {} #empty flow list
timeStamp = {} 
extFlowList = {}
intFlowList = {}
inByteCount = {}
oldInByteCount = {}
diffCountDict = {}

oldTime = datetime.now().strftime('%Y%m%d%H%M%S') 

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

def _handle_FlowRemoved (event):
    log.debug("_handle_FlowRemoved")
    if event.timeout:
        return
# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
    
    global flowList
    global extFlowList
    global intFlowList
    global inByteCount
    global oldInByteCount
    global timeStamp
    global diffCountDict

    #stats = flow_stats_to_list(event.stats)
    #log.debug("FlowStatsReceived from %s: %s", dpidToStr(event.connection.dpid), stats)
    
    #filter only connection from a monitoring node. use con.dpid
    if dpidToStr(event.connection.dpid) != '00-00-00-00-00-01': #if not switch s1
        return #do nothing, 

    #if Src_ip and Dst_ip from different flow are the same, combine count
    #Combine tx and rx flows into one stat record

    #NOTE:cookie differentiate if the flow is the same entry (cookie is unique for each flow)
    for f in event.stats:
        
        if f.priority in range(47470,47479): #flow of interest
            
            timeStamp[f.cookie] = datetime.now().strftime('%Y%m%d%H%M%S');
            #TEST:isolate and match ip 
            ip_src = str(f.match.nw_src)
            ip_dst = str(f.match.nw_dst)
            
            if(ip_dst.startswith('10.0.0') and  ip_src.startswith('10.0.0') ):
                log.debug("Internal Traffic %s <-> %s",ip_src,ip_dst)
                intFlowList[f.cookie] = f #store flow into list
            elif(ip_src.startswith('10.0.0')):
                log.debug("Outbound Traffic %s -> %s (%s bytes)",ip_src,ip_dst,f.byte_count)
                #if ip_src not in extFlowList:
                #extFlowList[ip_src] = {} #create sub-dict if doesnt exist
                #extFlowList[ip_src][f.cookie] = f #store flow into List
            elif(ip_dst.startswith('10.0.0')):
                log.debug("Inbound Traffic: %s <- %s (%s bytes)",ip_dst,ip_src,f.byte_count)


                if ip_dst not in extFlowList:
                    extFlowList[ip_dst] = {} #create sub-dict if doesnt exist
                extFlowList[ip_dst][f.cookie] = f #store flow into List

                if ip_src not in inByteCount:
                    inByteCount[ip_src] = {}
                d = inByteCount[ip_src]
                d[ip_dst] = f.byte_count
            
            
            if f.cookie in flowList:
                flowList[f.cookie] = f #update list (or do something about it)
            else:
                flowList[f.cookie] = f #add object to dict
   
    #dont write to file if empty 
    if not bool(flowList):
        return

    #write to file if a minute has passed  
    i = datetime.now().strftime('%Y%m%d%H%M%S') 
    global oldTime

    #if time passed more than 10 second
    if (int(i) - int(oldTime)) > 10 : 
        global oldTime
        oldTime = i;
        log.debug("Processing for time: " + i)

        """
        fileName = '/var/www/html/flowStat/' +i + '-flowStat.csv' 
        log.debug("write report %s" % fileName)
        with open(fileName, 'w') as csvfile:
            fieldnames = ['time','cookie','priority','timeout','duration_sec','nw_src','nw_dst','packet_count','byte_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
	    for key in flowList:
	        f = flowList[key]
		if f.priority in range(47470,47479): #flow of interest
			dl_src = f.match.dl_src
			dl_dst = f.match.dl_dst
			nw_src = f.match.nw_src
			nw_dst = f.match.nw_dst
			packet_count = f.packet_count
			time = timeStamp[f.cookie]
                        writer.writerow({'time':time,'cookie':f.cookie,'priority':f.priority,'timeout':f.hard_timeout,'duration_sec':f.duration_sec
                            ,'nw_src':nw_src,'nw_dst':nw_dst,'packet_count':packet_count,'byte_count':f.byte_count})
        
        fileName2 = '/var/www/html/externalFlow/extFlow-' +i +'.csv' 
        with open(fileName2, 'w') as csvfile:
            fieldnames = ['time','cookie','priority','timeout','duration_sec','nw_src','nw_dst','packet_count','byte_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
	    for ip in extFlowList:
	        flowDict = extFlowList[ip]
                for key in flowDict:
                    f = flowDict[key]
                    if f.priority in range(47470,47479): #flow of interest
                            dl_src = f.match.dl_src
                            dl_dst = f.match.dl_dst
                            nw_src = f.match.nw_src
                            nw_dst = f.match.nw_dst
                            packet_count = f.packet_count
                            time = timeStamp[f.cookie]
                            
                            writer.writerow({'time':time,'cookie':f.cookie,'priority':f.priority,'timeout':f.hard_timeout,'duration_sec':f.duration_sec,'nw_src':nw_src,
                                'nw_dst':nw_dst,'packet_count':packet_count,'byte_count':f.byte_count})

        fileName3 = '/var/www/html/externalFlow/inCount-' +i +'.csv' 
        with open(fileName3, 'w') as csvfile:
            fieldnames = ['ip_src','ip_dst','byte_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
            for ip_src in inByteCount:
                hostDict = inByteCount[ip_src]
                for ip_dst in hostDict:
                    count = hostDict[ip_dst]
                    writer.writerow({'ip_src':ip_src,'ip_dst':ip_dst,'byte_count':count})
        """

        fileName4 = '/var/www/html/externalFlow/diffCount-' +i +'.csv' 
        with open(fileName4, 'w') as csvfile:
            fieldnames = ['ip_src','ip_dst','diff_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
            for ip_src in inByteCount:
                hostDict = inByteCount[ip_src]
                
                for ip_dst in hostDict:
                    count = hostDict[ip_dst]
                    old_count = 0
                    try:
                        if ip_dst in oldInByteCount[ip_src]: # if the flow exist in past minute snapshot
                            old_count = oldInByteCount[ip_src][ip_dst]
                    except KeyError:
                            old_count = 0; 
                    diff_count = count - old_count
                    if diff_count != 0:
                        writer.writerow({'ip_src':ip_src,'ip_dst':ip_dst,'diff_count':diff_count})
                        if ip_src not in diffCountDict:
                            diffCountDict[ip_src] = {}
                        diffCountDict[ip_src][ip_dst] = diff_count;


        fileName6 = '/var/www/html/testTable.csv'	
        df = pd.DataFrame.from_dict(diffCountDict)
        with open(fileName6, 'w') as csvfile:	
            df.to_csv(fileName6)

        """
        Prepare Info Lists
        """
        log.debug("Retrieving info from params csv files...")
        servListRAW = tuple(open('/root/networkMonitor/servList.csv', 'r'))
        hostListRAW = tuple(open('/root/networkMonitor/hostList.csv', 'r'))

        servList = []
        hostList = []
        for i in servListRAW:
            servList.append(i.strip()) #remove \n character at the end of the line

        for i in hostListRAW:
            hostList.append(i.strip()) #remove \n character at the end of the line

        servName = {}
        hostName = {}

        with open('/var/www/html/hostName.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                hostName = row
        with open('/var/www/html/servName.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                servName = row

        with open('/var/www/html/quota.csv','r') as f:
            quota = int(f.read())

        """
        Update Record and stat
        """
        log.debug("Update csv record files...")

        i = 0

        usageDict = {}

        """ Read from a csv file"""
        with open('/var/www/html/usageRecord.csv', 'r') as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    #convert row into sub dict
                    #convert string to int
                    usageDict[servList[i]] = dict((k,int(v)) for k,v in row.iteritems())
                    
                    """Just access the number of servers (3)"""
                    i = i + 1
                    if i > 2:
                        i = 0
                except KeyError:
                    dummy = 1


        """
        Update usageDict
        """
        try:
            for serv in diffCountDict:
                servDict = diffCountDict[serv]
                for host in servDict:
                    usageDict[serv][host] = usageDict[serv][host] + servDict[host]
        except KeyError:
            print 'fatal error'


        """ Writing to a csv file"""

        with open('/var/www/html/usageRecord.csv', 'w') as csvfile:
            fieldnames = hostList
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for serv in servList:
                writer.writerow(usageDict[serv])

        #csv table for display with panda's magic
        fileName7 = '/var/www/html/totalUsage.csv'   
        df = pd.DataFrame.from_dict(usageDict)
        with open(fileName7, 'w') as csvfile:   
            df.to_csv(fileName7)


        """
        Prepare data for Plotting
        """
        log.debug("Stat calculation...")
        usageByServData = {} #create empty dictioinary for plotting 

        #summing for each Server Usage
        for i in servList:
            accuSum= 0 
            try:
                d = usageDict[i]
                for host in d:
                    count = d[host] 
                    accuSum = accuSum + count

                if accuSum > quota:
                    with open("/var/www/html/blockList.csv", "a") as myfile:
                        myfile.write(i)

                usageByServData[i] = accuSum
            except KeyError:
                usageByServData[i] = 0 #set to zero count if it does not exist. 


        usageByUserData = {}
        #summing for each User
        for host in hostList:
            accuSum = 0
            for serv in usageDict:
                try: 
                    accuSum = accuSum + usageDict[serv][host]
                except KeyError:
                    accuSum = accuSum
            if accuSum > quota:
                with open("/var/www/html/blockList.csv", "a") as myfile:
                    myfile.write(host)

            usageByUserData[host] = accuSum

        detailedUsagePerUser = {}
        for host in hostList:
            hostDict = {}
            for serv in usageDict:
                try:
                    hostDict[serv] = usageDict[serv][host]
                except KeyError:
                    dummy = 0
            detailedUsagePerUser[host] = hostDict


        """
        Vincent part
        """
        log.debug("Plotting...")
        #plot 1
        sites = []
        dataval = []
        sizes = [0] * len(usageByServData)

        j = 0
        for i in usageByServData:
            sites.append(servName[i])
            sizes[j] = usageByServData[i]
            dataval.append(sizes[j])
            j = j + 1

        columns = ['Data(Bytes)']
        #plot table to the right of the chart
        #plt.subplots_adjust(right= 0.75, top =0.85)
        #plot percentage to 2 decimal places
        plt.pie(sizes, labels = sites, autopct = '%.2f%%')
        #plot the legend of the pie chart instead of the table
        plt.legend(dataval,loc=(1.2, 0.4), shadow=True)
        plt.axis('equal')
        plt.draw()
        plt.title('Data Comsumption by website' , y = 1.08 )
        plt.savefig("/var/www/html/plotServ.png", bbox_iches = 'tight')
        plt.clf()

        #plot 2
        hosts = []
        dataval = []
        sizes = [0] * len(usageByUserData)

        j = 0
        for i in usageByUserData:
            hosts.append(hostName[i])
            sizes[j] = usageByUserData[i]
            dataval.append(sizes[j])
            j = j + 1

        plt.pie(sizes, labels = hosts, autopct = '%.2f%%')
        plt.axis('equal')
        plt.draw()
        plt.title('Data Comsumption by host' , y = 1.08 )
        plt.savefig("/var/www/html/plotHost.png" , bbox_iches = 'tight')
        plt.clf()

        #plot 3
        for serv in usageDict:
            userDict = usageDict[serv]
            hosts = []
            dataval = []
            sizes = [0] * len(userDict)

            j = 0
            for i in userDict:
                hosts.append(hostName[i])
                sizes[j] = userDict[i]
                dataval.append(sizes[j])
                j = j + 1

            plt.pie(sizes, labels = hosts, autopct = '%.2f%%')
            plt.axis('equal')
            plt.draw()
            plt.title('Data Comsumption for website ' + servName[serv] , y = 1.08 )
            plt.savefig("/var/www/html/servReport/serv"+ serv.replace (".", "_")+ ".png" , bbox_iches = 'tight')
            plt.clf()

        #plot 4
        for host in detailedUsagePerUser:
            servDict = detailedUsagePerUser[host]
            sites = []
            dataval = []
            sizes = [0] * len(servDict)

            j = 0
            for i in servDict:
                sites.append(servName[i])
                sizes[j] = servDict[i]
                dataval.append(sizes[j])
                j = j + 1

            columns = ['Data(Bytes)']

            #plot table to the right of the chart
            #plt.subplots_adjust(right= 0.75, top =0.85)
            #plot percentage to 2 decimal places
            plt.pie(sizes, labels = sites, autopct = '%.2f%%')
            #plot the legend of the pie chart instead of the table
            plt.legend(dataval,loc=(1.2, 0.4), shadow=True)
            plt.axis('equal')

            plt.draw()
            plt.title('Data Comsumption for user ' + hostName[host] ,y = 1.08 )
            plt.savefig("/var/www/html/userReport/user"+ host.replace (".", "_")+".png" , bbox_iches = 'tight')
            plt.clf()

        #save flow of the last time
        oldInByteCount = inByteCount

        #clear flow list afer write to file         
        flowList = {}	
        extFlowList = {}
        intFlowList = {}
        timeStamp = {}
        inByteCount = {}
        diffCountDict = {}

# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  #log.debug("PortStatsReceived from %s: %s", 
  #  dpidToStr(event.connection.dpid), stats)
    
# main functiont to launch the module
def launch ():
  from pox.lib.recoco import Timer

  global oldTime
  oldTime = datetime.now().strftime('%Y%m%d%H%M%S') 
  # attach handsers to listners
  core.openflow.addListenerByName("FlowRemoved",
    _handle_FlowRemoved)
  core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
  core.openflow.addListenerByName("PortStatsReceived", 
    _handle_portstats_received) 

  # timer set to execute every 1 seconds
  Timer(1, _timer_func, recurring=True)
