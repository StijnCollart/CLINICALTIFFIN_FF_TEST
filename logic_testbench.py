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

class LbTestbench():
    def __init__(self, resources):
        """ The testbench is initialized with using resource strings passed 
        from a dictionary. """

        #log start time
        self.starttime = datetime.datetime.now().isoformat('_') 

        #initialize instruments
        self.daq = Ks34972a(resources['daq'])
        self.counter = Ks53220a(resources['counter'])
        self.psu = Pst3202(resources['psu'])
        #self.scope = Dso6104(resources['scope'])
        #backchannel UART to the logic board, assuming 115200 baudrate.
        #don't mount the board until after everything is initialized
        
        #log current 

        self.log_setup_data()

        #Channel number for full word digital output writes:
        self.digital_base = 0x201

        #initial state of digital output port
        self.portstate = 0x0000
        self.daq.set_digital_out(self.digital_base, self.portstate)

        #digital output pin names and offsets
        self.digital_pins = {"QUADB" : 0x0001, \
                             "QUADA" : 0x0002, \
                             "QUADI" : 0x0004, \
                             "INJECT_CTL" : 0x0008, \
                             "STANDBY_CTL" : 0x0010, \
                             "CARTRIDGE_CTL" : 0x0020, \
                             "ESCON_READY" : 0x0040, \
                             "NTC_EN" : 0x0100, \
                             "NTC_A0" : 0x0200, \
                             "NTC_A1" : 0x0400, \
                             "LED_SW_EN" : 0x0800, \
                             "LED_SW_STATE" : 0x1000, \
                             "VOUT_A0" : 0x2000, \
                             "VOUT_A1" : 0x4000, \
                             "VOUT_A2" : 0x8000 }

        #analog input channel names and ranges
        self.analog_inputs = {"CONTACTOR_EN" : (101, 10), \
                              "CHARGE_EN" : (102, 10), \
                              "ESCON_EN" : (103, 10), \
                              "IMOTION" : (104, 1), \
                              "IVCC" : (105, 1), \
                              "IBAT" : (106, 1), \
                              "ISYS" : (106, 1), \
                              "IBUS" : (108, 1), \
                              "VBUS" : (111, 10), \
                              "PP3V0_MICRO" : (112, 10), \
                              "PP3V0_MOTION" : (113, 10), \
                              "I2C_SDA" : (114, 10), \
                              "I2C_SCL" : (115, 10), \
                              "VCELL" : (116, 10), \
                              "UI_POWER" : (117, 10), \
                              "VSYS" : (118, 10), \
                              "PP5V0_ESCON" : (119, 10), \
                              "ESCON_POWER_EN" : (120, 10) }

        #analog output channel names
        self.analog_outputs = {"VBAT" : 204, \
                               "VMUX" : 205 }

        #shared analog channel names and addresses
        self.muxchannels = {"IMICRO" : 3, \
                            "IMOTION" : 4, \
                            "ISYS" : 2, \
                            "IMOTOR" : 1, \
                            "VCAP_DIV" : 0, \
                            "VMOTOR_DIV" : 5}

    def log_setup_data(self):
        

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

    def set_vbat(self, vbat):
        vbat = vbat / 10.0
        self.write_voltage_out(self.analog_outputs["VBAT"], vbat)
        return 0

    def set_analog_output(self, channel_name, voltage):
        if "VBAT" == channel_name : 
            self.set_vbat(voltage)
        else:
            #disable mux
            #set output voltage
            #set mux channel and enable mux
