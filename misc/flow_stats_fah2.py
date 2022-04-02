#!<path-to-your-anacaonda-python>
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

# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()
flowList = {} #empty flow list
timeStamp = {} 
extFlowList = {}
intFlowList = {}
inByteCount = {}
oldInByteCount = {}

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

    stats = flow_stats_to_list(event.stats)
    #log.debug("FlowStatsReceived from %s: %s", dpidToStr(event.connection.dpid), stats)
    
    #TODO:filter only connection from a monitoring node. use con.dpid
    if dpidToStr(event.connection.dpid) != '00-00-00-00-00-01': #if not switch s1
        return #do nothing, 

    #TODO:if Src_ip and Dst_ip from different flow are the same, combine count
    #TODO:Combine tx and rx flows into one stat record

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

        fileName4 = '/var/www/html/externalFlow/diffCount-' +i +'.csv' 
        with open(fileName4, 'w') as csvfile:
            fieldnames = ['ip_src','ip_dst','diff_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
            for ip_src in inByteCount:
                hostDict = inByteCount[ip_src]
                #diffCount_dictSer = inByteCount[ip_src]
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
                        #diffCount_dictSer[ip_src] = diff_count
						


        servList = tuple(open('/root/networkMonitor/servList.csv', 'r'))
        hostList = tuple(open('/root/networkMonitor/hostList.csv', 'r'))
        
        #TODO: write file into nice format
        #repeat same file to show 
		
        """
        fileName5 = '/var/www/html/testTable.csv' 
        with open(fileName5, 'w') as csvfile:
            fieldnames = ['ip_src','ip_dst','diff_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 
            """
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
                diff_count = count -  old_count
                if diff_count != 0:
                    diff_count = 0 #dummy line
                    #writer.writerow({'ip_src':ip_src,'ip_dst':ip_dst,'diff_count':diff_count})
                       	
						
						
		fileName6 = '/var/www/html/testTable.csv'	
		df = pd.DataFrame.from_dict(inByteCount)
		with open(fileName6, 'w') as csvfile:	
			df.to_csv(fileName6)
			
		AccuCountSer1 = 0
		AccuCountSer2 = 0
		AccuCountSer3 = 0		

		"""
		fileName7 = '/var/www/html/externalFlow/AccumulatedByteOverTimeServer.csv' 
        with open(fileName7, 'w') as csvfile:
			fieldnames = ['Time','Server1','Server2','Server3']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()  
					
			for ip_src in inByteCount:
				hostDict = inByteCount[ip_src]
				diffCount_dictSer = inByteCount[ip_src]
				for ip_dst in hostDict:
					count = hostDict[ip_dst]
					old_count = 0
					try:
						if ip_dst in oldInByteCount[ip_src]: # if the flow exist in past minute snapshot
							old_count = oldInByteCount[ip_src][ip_dst]
					except KeyError:
							old_count = 0; 
					diff_count = count -  old_count
					if diff_count != 0:
						diffCount_dictSer[ip_src] = diff_count			
						
			sumDiffCount_dictSer = defaultdict(int)
			for d in diffCount_dictSer:
				sumDiffCount_dictSer[d['ip_src']] += d['diffCount']			
						
			[{'ip_src': ip_src, 'diffCount': diffCount} for ip_src, diffCount in sumDiffCount_dictSer.items()]
						
			for ip_src in sumDiffCount_dictSer:
				if ip_src == '10.46.42.3':
					AccuCountSer1 = diffCount	
				if ip_src == '10.46.42.1':
					AccuCountSer2 = diffCount
				if ip_src == '10.123.123.123':
					AccuCountSer3 = diffCount		 	
				writer.writerow({'Time':i,'Server1':AccuCountSer1,'Server2':AccuCountSer2,'Server3':AccuCountSer3})
			
			
		"""
		
        #save flow of the last time
        oldInByteCount = inByteCount

        #clear flow list afer write to file         
        flowList = {}	
        extFlowList = {}
        intFlowList = {}
        timeStamp = {}
        inByteCount = {}
"""
    # Get number of bytes/packets in flows for web traffic only
    web_bytes = 0
    web_flows = 0
    web_packet = 0
    for f in event.stats:
        if f.match.tp_dst == 80 or f.match.tp_src == 80:
          web_bytes += f.byte_count
          web_packet += f.packet_count
          web_flows += 1
        log.info("Web traffic from %s: %s bytes (%s packets) over %s flows", 
        dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)
"""

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

  # timer set to execute every 0.5 seconds
  Timer(1, _timer_func, recurring=True)
