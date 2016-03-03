import serial

class Logicboard():
    """ Abstraction layer to control the logic board over UART/USB """
    def __init__(self, resource):
        """connect to the logic board over UART using the vcp identified by
        'resource' """
        #open serial port
        self.ser = serial.Serial(resource, 115200)
        #get the unique ID of the board
        self.get_id()

    def die(self):
        """ closes the VCP """
        self.ser.close()

    def send_command(self, command):
        """ Send a command to the logic board and get a response.
        Return either a requested value or 0 (success) or -1 (error) """
        #flush out the serial port's rx buffer
        self.ser.flush()
        #send the command. Specific format to be discussed with Jason
        txstr = "foobar\r\n"
        self.ser.write(txstr)
        #read from logic board until \r\n.
        #result in the format {VALUE}:[OK|ER]\r\n
        #{VALUE} should be 0 if no value is returned.
        rxstr = ""
        while not "\r\n" in rxstr:
            rxstr += self.ser.read(self.ser.inWaiting())
        res_ls = rxstr.strip("\r\n").split(":")
        res = [-1,res_ls[0]]["OK"==res_ls[-1]]
        if res < 0:
            print "Error: Logic Board returned %s\r\n"%res_ls[0]
        return res
        
    def get_id(self):
        """ get the unique ID of the board, whether that's a serial 
        number we program, the unique hardware ID of the micro, or both. """
        return self.command("get_id")

    def set_testclk_8mhz(self):
        """ turn on the testclk pin and connect the HSE clock the pin """
        return self.command("testclk_8mhz_on")

    def set_testclk_32khz(self):
        """ turn on the testclk pin and connect the HSE clock the pin """
        return self.command("testclk_32khz_on")
    
    def testclk_off(self):
        """ set the testclk pin to hi-z """
        return self.command("testclk_off")

    def read_adc(self, channel):
        """ read the indicated channel from ADC1 """
        return self.command("adcread:%s"%channel)

    def read_rtc(self):
        """ Read the current unix timestamp from the RTC """
        return self.command("rtcread")
    
    def set_rtc(self, timestamp):
        """ Updates the RTC with the given unix timestamp """
        return self.command("rtcset:%s"%timestamp)

    def enable_3v0_motion(self):
        """ turns on load switch to enable PP3V0_Motion """
        return self.command("vmotion_on")

    def disable_3v0_motion(self):
        """ turns off the load switch to disable PP3V0_Motion """
        return self.command("vmotion_off")

    def vmotor_on(self):
        """ drives ESCON_POWER_EN high """
        return self.command("vmotor_on")

    def vmotor_off(self):
        """drives ESCON_POWER_EN low """
        return self.command("vmotor_off")

    def opto_bypass_on(self):
        """ drives opto_bypass high """
        return self.command("opto_bypass_on")
    
    def opto_bypass_off(self):
        """ drives opto_bypass low """
        return self.command("opto_bypass_off")

    def contactor_enable(self):
        """ drive LB2PB_CONTACTOR_EN high """
        return self.command("contactor_on")
    
    def contactor_disable(self):
        """ drive LB2PB_CONTACTOR_EN low """
        return self.command("contactor_off")

    def escon_enable(self):
        """ drive LB2PB_ESCON_EN high """
        return self.command("escon_enable")
    
    def escon_disable(self):
        """ drive LB2PB_ESCON_EN low """
        return self.command("escon_disable")

    def capcharge_enable(self):
        """ drive LB2PB_CAP_CHARGE_EN low """
        return self.command("capcharge_on")

    def capcharge_disable(self):
        """ drive LB2PB_CAP_CHARGE_EN high """
        return self.command("capcharge_off")

    def get_quad_state(self):
        """ return the state of the quadrature encoder lines QUADA (0x01),
        QUADB (0x02), and QUADI (0x04) """
        return self.command("get_quad_state")

    def get_escon_ready_state(self):
        """ reads the state of the escon_ready input """
        return self.command("escon_ready_state")

    def get_switch state(self):
        """ returns the state of the cartridge (0x01), standby (0x02), and
        inject (0x04) switches """
        return self.command("switch_state")

    def get_charger_state(self):
        """ returns the state of the ~CHG_PG (0x01) and ~CHG (0x02) lines """
        return self.command("charger_state")

    def watchdog_on(self):
        """ turns on the ~WD_EN line to enable the watchdog and starts kicking
        the dog """
        return self.command("watchdog_on")

    def watchdog_off(self):
        """ disables the ~WD_EN line """
        return self.command("watchdog_off")

    def get_pg_state(self):
        """ returns the state of the PHOTO_BH (0x01) and PHOTO_FH (0x02) 
        lines """
        return self.command("photogate_state")
        
    def enter_standby(self):
        """ puts the board into standby (lowest power state) after 1s delay """
        return self.command("enter_standby")
