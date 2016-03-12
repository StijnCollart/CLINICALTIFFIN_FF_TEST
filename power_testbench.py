import sys
import time
import datetime

if not "../measurement" in sys.path:
    sys.path.append("../measurement")

#import power supply
from pst3202 import Pst3202
#import DAQ
from keysight_34972a_daq import Ks34972a
#import frequency counter
from keysight_53220a_counter import Ks53220a

class PbTestbench():
    def __init__(self, resources):
        """ The testbench is initialized with using resource strings passed 
        from a dictionary. """

        #log start time
        self.starttime = datetime.datetime.now().isoformat('_') 

        #initialize instruments
        self.daq = Ks34972a(resources['daq'])
        #self.counter = Ks53220a(resources['counter'])
        self.psu = Pst3202(resources['psu'])
        self.scope = Dso6104(resources['scope'])
        self.arb = Bk4053(resources['arb'])

        self.log_setup_data()

        #Channel number for full word digital output writes:
        self.digital_base = 0x201

        #initial state of digital output port
        self.portstate = 0x0000
        self.daq.set_digital_out(self.digital_base, self.portstate)

        #digital output pin names and offsets
        self.digital_pins = {"MOTOREN" : 0x0001, \
                             "CONTACTOR_EN" : 0x0002, \
                             "nCAPCHG_EN" : 0x0004, \
                             "ESCON_EN" : 0x0008, \
                             "CH1_A0" : 0x0010, \
                             "CH1_A1" : 0x0020, \
                             "CH2_A0" : 0x0040, \
                             "CH2_A1" : 0x0100 }

        #analog input channel names and ranges
        self.analog_inputs = {"ESCON_READY" : (101, 10), \
                              "VMOTOR_DIV" : (102, 10), \
                              "PP5V0_ESCON" : (103, 10), \
                              "VMOTOR" : (104, 100), \
                              "IMOTOR" : (105, 10), \
                              "VCAP_SNS" : (106, 100), \
                              "VCAP_DIV" : (107, 10), \
                              "Q4_DRAIN" : (108, 10), \
                              "Q3_GATE" : (109, 10), \
                              "Q4_GATE" : (110, 10), \
                              "Q4_SOURCE" : (111, 10), \
                              "nSHDN" : (112, 10), \
                              "Q6_SOURCE" : (113, 10), \
                              "ISYS" : (114, 1), \
                              "VSYS" : (115, 10), \
                              "IBAT" : (116, 1) }

        #muxed oscilloscope channel names and addresses
        self.mux1channels = {"VMOTOR" : 0, \
                            "IMOTOR" : 1, \
                            "CONTACTOR_EN" : 2, \
                            "VSYS" : 3 }
        self.mux2channels = {"VCAP" : 0, \
                             "ESCON_PWM" : 1, \
                             "PWR_EN" : 2 }

    def log_setup_data(self):
        """ record serial numbers and such from connected equipment """
        logfile = "%s_PowerFixture_EquipmentLog.txt"%self.starttime
        self.daq.log_id(logfile)
        self.psu.log_id(logfile, append = True)
        self.scope.log_id(logfile, append = True)
        self.arb.log_id(logfile, append = True)

    def select_scope_signal(self, signame):
        if signame in self.mux1channels.keys():
            a0 = "CH1_A0"
            a1 = "CH1_A1"
            addr = self.mux1channels[signame][1]
        elif signame in self.mux2channels.keys():
            a0 = "CH2_A0"
            a1 = "CH2_A1"
            addr = self.mux2channels[signame][1]
        else:
            return -9999999999999

        #set scope channel select
        if addr & 0x01:
            self.set_digital_pin(self, a0)
        else:
            self.clear_digital_pin(self, a0)

        if addr & 0x02:
            self.set_digital_pin(self, a1)
        else:
            self.clear_digital_pin(self, a1)
        
        return 0

    def set_digital_pin(self, pin_name):
        """ Set a digital output high """
        pin_offset = self.digital_pins[pin_name]
        #set the pin in the shadow register
        self.portstate = self.portstate | pin_offset
        #update the daq's digital output with the shadowed value
        self.daq.set_digital_out(self.digital_base, self.portstate)
        return 0

    def clear_digital_pin(self, pin_name):
        pin_offset = self.digital_pins[pin_name]
        #clear the pin state in the shadow register
        self.portstate = self.portstate & (~pin_offset)
        #update the daq's digital output with the shadowed value
        self.daq.set_digital_out(self.digital_base, self.portstate)
        return 0

    def get_analog_inputs(self, channel_list):
        scan_channels = []
        vrange = None
        #build up the scan list
        for item in channel_list:
            channel = self.analog_inputs[item]
            #Check that we are reading compatible (same scale) inputs
            if range:
                if channel[1] != vrange:
                    print "WARNING! Scan list should have the same range!")
                    range = max(vrange, channel[1])
            else:
                vrange = channel[1]
            scan_channels.append(channel[0])
        #scan channels and return the list of values
        return get_vdc(scan_channels, vrange)
