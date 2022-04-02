#!/bin/bash          
echo script run POX Controller
sudo killall controller
sudo mn -c
cd ~/pox
./pox.py log.level --DEBUG misc.project_switch misc.flow_stats_fah2


