#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 Chayut, Thanchanok, Vincent, Michale
# Q2hheXV0T3JhcGlucGF0aXBhdA==
#

"""
"""

# standard includes
#from pox.core import core
#from pox.lib.util import dpidToStr
#import pox.openflow.libopenflow_01 as of
#from pox.lib.addresses import IPAddr
import csv
import os
import glob
import json
from datetime import datetime


def _handle_flowstats_received ():


		

	data_list = []	
	host1_ip = '10.0.0.1'	
	for i in range (2,7):
		i = str(i)
		fileName = '/root/networkMonitor/dataManipulation/flowstats/' +'20150518035' +i + '-flowStat.csv' 
		#log.debug("write report %s" % fileName)
		
		input_file = csv.DictReader(open(fileName))
		for row in input_file:
			
			
			#{'packet_count': '2158', 'nw_dst': '10.0.0.2', 'byte_count': '5842276', 'priority': '47471', 'duration_sec': '14', 'cookie': '140087', 'timeout': '15', 'time':'20150518035600', 'nw_src': '10.0.0.4'}
			#{'packet_count': '2158', 'nw_dst': '10.0.0.2', 'byte_count': '5842276', 'priority': '47471', 'duration_sec': '14', 'cookie': '140087', 'timeout': '15', 'time':'20150518035600', 'nw_src': '10.0.0.4'}
			
		
			data_list.append(row)
			
	#print data_list	
	'''
	with open('ReportHost1.csv', 'w') as csvfile:
				fieldnames = ['time','cookie','priority','timeout','duration_sec','nw_src','nw_dst','packet_count','byte_count']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader() 
	'''			
	
	for row in data_list:
		ip_src = row.get('nw_src')
		
		if ip_src == '10.0.0.1':
			
			time = row.get('time')
			cookie = row.get('cookie')
			priority = row.get('priority')
			timeout = row.get('timeout')
			duration_sec = row.get('duration_sec') 
			nw_src = row.get('nw_src') 
			nw_dst = row.get('nw_dst')
			packet_count = row.get('packet_count') 
			byte_count = row.get('byte_count') 

			array = [time,cookie,priority,timeout, duration_sec, nw_src,nw_dst, packet_count,byte_count]
			
			
			
			
			
				
			with open('ReportHost1.csv', 'a') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(array)
			
			
			array = []

	
			
	
			
			
			
			
_handle_flowstats_received ()		
		