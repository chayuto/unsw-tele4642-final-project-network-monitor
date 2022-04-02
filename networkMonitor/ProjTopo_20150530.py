#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
	
class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1,linkopts2,linkopts3,fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self,**opts)
    

	k = fanout	
	
	Switch1 = self.addSwitch ('s1')
	Switch2 = self.addSwitch ('s2')		
	self.addLink(Switch1,Switch2, **linkopts1)
	      
	#add hosts
	Host1 = self.addHost('h1', cpu=.5/k)
	self.addLink(Switch1,Host1, **linkopts3)
	Host2 = self.addHost('h2', cpu=.5/k)
	self.addLink(Switch1,Host2, **linkopts3)
	Host3 = self.addHost('h3', cpu=.5/k)
	self.addLink(Switch1,Host3, **linkopts3)	
	Host4 = self.addHost('h4', cpu=.5/k)
	self.addLink(Switch1,Host4, **linkopts3)
	
	#add servers
	Server1 = self.addHost('ser1', cpu=.5/k)
	self.addLink(Switch2,Server1, **linkopts3)
	Server2 = self.addHost('ser2', cpu=.5/k)
	self.addLink(Switch2,Server2, **linkopts3)
	Server3 = self.addHost('ser3', cpu=.5/k)
	self.addLink(Switch2,Server3, **linkopts3)	
			

def perfTest():
    "Create network and run simple performance test"
    linkCore= dict(bw=1000, delay='1ms', loss=1, max_queue_size=4000, use_htb=True)
    linkAgg = dict(bw=100, delay='2ms', loss=1, max_queue_size=2000, use_htb=True)
    linkEdge = dict(bw=10, delay='4ms', loss=1, max_queue_size=1000, use_htb=True)
   
    topo = CustomTopo(linkCore,linkAgg,linkEdge,fanout=2)
    net = Mininet(topo=topo,build= False,host=CPULimitedHost,link=TCLink,autoSetMacs = True)
    odl_ctrl = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    net.build()
    net.start() 
    #set IP
    ser1 = net.get('ser1')
    ser1.setIP('10.46.42.1')
    ser2 = net.get('ser2')
    ser2.setIP('10.123.123.123')
    ser3 = net.get('ser3')
    ser3.setIP('10.46.42.3')

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
   
   
    print "Testing network connectivity"
    for i in range(0,2):
        net.iperf([h1,h2],port = 443,seconds = 1)
        net.iperf([h1,ser1],port = 80,seconds = 1)
        net.iperf([h1,ser2],port = 443,seconds = 1)
        net.iperf([h1,ser3],port = 443,seconds = 1)

    for i in range(0,2):   
        net.iperf([h2,ser1],port = 80,seconds = 1)
        net.iperf([h2,ser2],port = 80,seconds = 1)
        net.iperf([h2,ser3],port = 443,seconds = 1)

    for i in range(0,2):
        net.iperf([h3,ser1],port = 433,seconds = 1)
        net.iperf([h3,ser2],port = 80,seconds = 1)
        net.iperf([h3,ser3],port = 80,seconds = 1)

    for i in range(0,2):
        net.iperf([h4,ser1],port = 443,seconds = 1)
        net.iperf([h4,ser2],port = 80,seconds = 1)
        net.iperf([h4,ser3],port = 80,seconds = 1)	

    for i in range(0,2):
        net.iperf([h1,ser1],port = 443,seconds = 1)
        net.iperf([h2,ser1],port = 80,seconds = 1)
        net.iperf([h3,ser1],port = 80,seconds = 1)	
        net.iperf([h4,ser1],port = 80,seconds = 1)
        
    for i in range(0,2):
        net.iperf([h1,ser2],port = 443,seconds = 1)
        net.iperf([h2,ser2],port = 80,seconds = 1)
        net.iperf([h3,ser2],port = 443,seconds = 1)	
        net.iperf([h4,ser2],port = 80,seconds = 1)	

    #some random things 	
    for i in range(0,2):
        net.iperf([h3,h2],port = 443,seconds = 2)
        net.iperf([h1,ser3],port = 80,seconds = 2)
        net.iperf([h4,ser3],port = 80,seconds = 2)
        net.iperf([h2,ser1],port = 443,seconds = 7)
        net.iperf([h4,ser3],port = 80,seconds = 7)
        net.iperf([h4,h2],port = 1433,seconds = 7)
    net.iperf([h3,ser1],port = 443,seconds = 7)
    net.iperf([h3,ser1],port = 443,seconds = 5)
    net.iperf([h4,ser2],port = 80,seconds = 7)

    #host = net.getNodeByName('h2')
    #host.sendCmd('python myHTTPServer.py -80')
    #print(host.IP())
    CLI(net)
    #net.interact()
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
