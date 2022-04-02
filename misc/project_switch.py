"""
TELE4642 StatLogger  based on original L2 Lerning switch
Copyright 2015 Chayut, Thanchanok, Vincent, Michale
Q2hheXV0T3JhcGlucGF0aXBhdA==
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool

from pox.lib.addresses import EthAddr
from pox.lib.packet.ethernet import ethernet
import pox.lib.packet as pkt

from random import randint
import time

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0

class LearningSwitch (object):

  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    log.debug("Initializing LearningSwitch, transparent=%s",
              str(self.transparent))

  def _handle_PacketIn (self, event):
    """
    Handle packet in messages from the switch to implement above algorithm.
    """
    #log.debug("=========================================")
    #log.debug("_handle_PacketIn")
    #log.debug("Connection %s" % (event.connection,))
    packet = event.parsed

    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
        log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      """
      Drops this packet and optionally installs a flow to continue
      dropping similar ones for a while
      """
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        msg.priority =  5000
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port  
        msg.priority =  5000
        self.connection.send(msg) #sned message to switch
  
  
    
    
    def normal_l2_op():
        # 6 - installing dlow
        log.debug("Installing flow for %s.%i -> %s.%i" %(packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        #TODO:modify match
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 60
        msg.priority =  5000 #not importantin not exact match
        msg.cookie = randint(1,9999999) #set flow ID
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
        
    def new_primary_flow():
        # 6 - installing dlow
        log.debug("Installing Primary flow for %s.%i -> %s.%i" %(packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        #packet.find("ipv4").srcip, packet.find("tcp").srcport, packet.find("ipv4").dstip, packet.find("tcp").dstport
        msg.match = msg.match = of.ofp_match()
        msg.match.in_port = event.port
        msg.match.dl_src = packet.src
        msg.match.dl_dst = packet.dst
        msg.match.dl_type = pkt.ethernet.IP_TYPE
        #msg.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        msg.match.nw_src = packet.find("ipv4").srcip
        msg.match.nw_dst = packet.find("ipv4").dstip
        #msg.match.tp_src = packet.find("tcp").srcport
        #msg.match.tp_dst = packet.find("tcp").dstport
        msg.cookie = randint(1,999999) #set flow ID
        msg.idle_timeout = 3600
        msg.hard_timeout = 3600
        msg.priority =  47471
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
   
   
    def new_secondary_flow():
        # 6 - installing dlow
        log.debug("Installing Secondary flow for %s.%i -> %s.%i" %(packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = msg.match = of.ofp_match()
        msg.match.in_port = event.port
        msg.match.dl_src = packet.src
        msg.match.dl_dst = packet.dst
        msg.match.dl_type = pkt.ethernet.IP_TYPE
        #msg.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        msg.match.nw_src = packet.find("ipv4").srcip
        msg.match.nw_dst = packet.find("ipv4").dstip
        #msg.match.tp_src = packet.find("udp").srcport
        #msg.match.tp_dst = packet.find("udp").dstport
        msg.idle_timeout = 3600
        msg.hard_timeout = 3600
        msg.cookie = randint(1,999999) #set flow ID
        msg.priority =  47470
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)

    def block_flow():
        # 6 - installing dlow
        log.debug("Block flow for %s.%i -> %s.%i" %(packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = msg.match = of.ofp_match()
        msg.match.in_port = event.port
        msg.match.dl_src = packet.src
        msg.match.dl_dst = packet.dst
        msg.match.dl_type = pkt.ethernet.IP_TYPE
        #msg.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        msg.match.nw_src = packet.find("ipv4").srcip
        msg.match.nw_dst = packet.find("ipv4").dstip
        #msg.match.tp_src = packet.find("udp").srcport
        #msg.match.tp_dst = packet.find("udp").dstport
        msg.idle_timeout = 3600
        msg.hard_timeout = 3600
        msg.cookie = randint(1,999999) #set flow ID
        msg.priority =  50000
        msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
        
    #################
    #  Start Operation
    #################
    self.macToPort[packet.src] = event.port # 1

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        
            
        #=============
        # L3 
        #=============
        packet = event.parsed # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        packet_in = event.ofp # The actual ofp_packet_in message.
        
        log.debug("[*] The packet in port is: %s" % (packet_in.in_port,))
        
        if packet.type == ethernet.IP_TYPE:
            #if ip in policy file
            if packet.find("tcp") or packet.find("udp"):
              blockList = tuple(open('/var/www/html/blockList.csv', 'r'))

              if packet.find("ipv4").srcip in blockList or packet.find("ipv4").dstip in blockList:
                block_flow()
                
              else:
                lines = tuple(open('/var/www/html/servList.csv', 'r'))
                if packet.find("ipv4").srcip in lines or packet.find("ipv4").dstip in lines:
                  log.debug("match list")
                  new_primary_flow()
            
                else:
                  log.debug("does not match list")
                  new_secondary_flow()

            #assume ipv4 only
            #ipv4_packet = event.parsed.find("ipv4")
            
              if packet.find("tcp"):
                  log.debug("tcp found: %s:%s to %s:%s", packet.find("ipv4").srcip, packet.find("tcp").srcport, packet.find("ipv4").dstip, packet.find("tcp").dstport)
                  
              elif packet.find("udp"):
                  log.debug("udp found: %s:%s to %s:%s", packet.find("ipv4").srcip, packet.find("udp").srcport, packet.find("ipv4").dstip, packet.find("udp").dstport)
            else:
	    	      normal_l2_op() 
        else:
            log.debug("Other Packet Type")
            normal_l2_op()


class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s, Switch %s" % (event.connection,event.dpid))
    LearningSwitch(event.connection, self.transparent)

    #mod flow for DNS packet
    #msg = of.ofp_flow_mod()
    #msg.match = of.ofp_match()
    #msg.match.dl_type = pkt.ethernet.IP_TYPE
    #msg.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
    #msg.match.tp_src = 53
    #msg.actions.append(of.ofp_action_output(port = of.OFPP_CONTROLLER))
    #event.connection.send(msg)


  #def _handle_PacketIn(self, event):
    #not important in Firefall application

def launch (transparent=False, hold_down=_flood_delay):
  """
  Starts an L2 learning switch.
  """
  log.debug("Start L2 learning switch")
  
  #import pox.log.color
  #pox.log.color.launch()
  #import pox.log
  #pox.log.launch(format="[@@@bold@@@level%(name)-23s@@@reset] " +
  #                                      "@@@bold%(message)s@@@normal")
  #import pox.log.level
  #pox.log.level.launch(**kw)
  
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
