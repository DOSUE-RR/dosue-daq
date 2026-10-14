#!/usr/bin/env python
# APSYN420 cannot select the output power strength.
import os, sys
import argparse
import datetime
import pathlib
import math
import struct
import time
from time import sleep

import socket
import numpy as np

IP_ADDRESS = '10.10.10.5'
PORT = 18
TIMEOUT = 10

class APSYN420:
    def __init__(self, host_ip=IP_ADDRESS, port=PORT, timeout=TIMEOUT, verbose=0):
        self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host_ip = host_ip
        self._port = port
        self._connected = False
        self._timeout = timeout
        self._verbose = verbose

    def __del__(self):
        if self._connected:
            self.close()

    def _print(self, message, verbose_threshold=-1):
        if self._verbose > verbose_threshold:
            print(message)
            pass

    def _w(self, word):
        word += '\n'
        #print(f'{word}')
        self._soc.send(word.encode())

    def _r(self):
        ret_msg = ''
        end     = '\n'
        while True:
            try:
                rcvmsg = self._soc.recv(1024).decode()
                self._print(f'APSYN420:_r(): raw rcvmsg = {rcvmsg}', 1)
            except Exception as e:
                print(f'APSYN420:_r(): Error! {e}')
                return None
            ret_msg += rcvmsg
            if rcvmsg[-1] == end :
                break
        self._print(f':_r(): ret_msg = {ret_msg}', 1)
        return ret_msg.strip()

    def _wr(self, word):
        self._print(f'APSYN420:_wr(): command = {word}', 1)
        self._w(word)
        r = self._r()
        if r is None :
            print(f'APSYN420:_wr(): Error! Failed to read for the command: "{word}"')
            print(f'APSYN420:_wr(): Error!  --> Socket connection is closed and exit')
            self._soc.close()
            return None
            pass
        return r

    def _wait(self):
        self._w('*WAI')

    def print_status(self):
        self._print('APSYN420:pring_status(): Device identification ='+ self._wr('*IDN?'))
        self._print('APSYN420:pring_status(): System Error ='+ self._wr('SYST:ERR?'))
        self._print('APSYN420:pring_status(): Event Status ='+ self._wr('*ESR?'))
        ##print('APSYN420:pring_status(): SYST:LANG ='+ self._wr('SYST:LANG?'))

    def print_error(self):
        self._print('APSYN420:pring_error(): System Error ='+ self._wr('SYST:ERR?'))

    def default_setting(self):
        self._print('APSYN420:default_setting(): ')
        self._print('APSYN420:default_setting(): *** Original status ***')
        self.print_status()
        self._print('APSYN420:default_setting(): ')
        self._print('APSYN420:default_setting(): *** Initialize settings')
        self._w('*CLS') # clear
        self._w('*RST') # reset
        ##self._w('SYST:LANG SCPI')
        self._print('APSYN420:default_setting(): ')
        self._print('APSYN420:default_setting(): *** Current status ***')
        self.print_status()
        self._print('APSYN420:default_setting(): ')
        self.print_error()
        self._wait()

    def connect(self):
        if self._connected:
            raise Exception("Already connected.")
        self._soc.connect((self._host_ip, self._port))
        self._connected = True
        self._soc.settimeout(self._timeout)
        self.default_setting()

    def close(self):
        if self._connected:
            self._soc.close()
            self._connected = False

    ## Signal power ON
    def powerON(self):
        self._w(f'OUTP:STAT ON')
    ## Signal power OFF
    def powerOFF(self):
        self._w(f'OUTP:STAT OFF')

    # Frequency
    @property
    def freq(self) :
        freq = float(self._wr('FREQ?')) # [Hz]
        #print(freq)
        return freq # [Hz]
    @freq.setter
    def freq(self, freq_Hz): # [Hz]
        freq_Hz = int(freq_Hz)
        #print(freq_Hz)
        self._w(f'FREQ {freq_Hz}')

    # Reference
    def ref(self): # [Hz]
        ref_freq_Hz = 10000000 # Ref output from SPA: 10MHz
        #print(freq_Hz)
        self._w(f'ROSC:SOUR EXT')
        #sleep(10)
        self._wr('ROSC:SOUR?')
        self._w(f'ROSC:EXT:FREQ {ref_freq_Hz}')
        #sleep(10)
        self._wr('ROSC:EXT:FREQ?')
        self._wr('ROSC:LOCK?')

    # Power
    #@property
    #def power(self) :
    #    return float(self._wr('POW?')) # [dBm]
    #@power.setter
    #def power(self, power_dB): # [dBm]
    #    self._w(f'POW {power_dB}')

    #@property
    #def power_W(self) :
    #    dBm =  float(self._wr('POW?')) # [W]
    #    return 1.0e-3*(10.**(dBm*0.1)) # dBm --> W
    #@power_W.setter
    #def power_W(self, W): # [W]
    #    dBm = np.log10(W*1.0e+3)*10. # W --> dBm
    #    self._w(f'POW {dBm}')

'''
    # Phase default 0 rad !!!!!!!!!!!!!!!here!!!!!!!!!!!!!!!!!!!
    def phase(self):
        self._w(f'PHAS:REF')
'''



def main(onoff = False, # True:ON, False:OFF
         freq = 20.e+9,  # Hz
         power_dBm = None, # dBm
         power_W   = None, # W
         ip_address = IP_ADDRESS,
         port = PORT,
         verbose = 0):

    # Initialize connection
    sg = APSYN420(host_ip=ip_address, port=port, verbose=verbose)
    sg.connect()

    # Setting configuration
    sg.freq = freq
    if power_dBm is not None and power_W is None:
        print('main(): WARNING! APSYN420 does NOT have a function to change the power.')
        sg.power = power_dBm
    elif power_W is not None and power_dBm is None:
        print('main(): WARNING! APSYN420 does NOT have a function to change the power.')
        sg.power_W = power_W
    elif power_W is not None and power_dBm is not None:
        print('main(): WARNING! One of power_W or power_dBm should be specified!')
        print('main(): power_dBm = {power_dBm}, power_W = {power_W}')
        return -1
    else:
        pass

    print(f'frequency = {sg.freq} [Hz]')
    #print(f'power = {sg.power} [dBm]')
    #print(f'power = {sg.power_W} [W]')
    #print(f'phase = {sg.phase()} [rad]')

    # Power ON/OFF
    if onoff:
        print(f'Power ON')
        sg.powerON()
        sg.ref() # Set reference

    else:
        print(f'Power OFF')
        sg.powerOFF()
        pass

    del sg
    print('End')
    return 0


if __name__ == '__main__':
    # Default settings
    freq = 20.e+9  # Hz
    dBm  = None # dBm
    W = None # W

    parser = argparse.ArgumentParser()
    parser.add_argument('--on', action='store_true', default=False, help=f'Power ON (NOTE: Must select --on or --off)')
    parser.add_argument('--off', action='store_true', default=False, help=f'Power OFF (NOTE: Must select --on or --off)')
    parser.add_argument('-f', '--freq', dest='freq', type=float, default=freq, help=f'Frequency [Hz] (default: {freq})')
    #parser.add_argument('-p', '--power_dBm', dest='power_dBm', type=float, default=dBm,
    #                    help=f'RF power [dBm] NOTE:One of power_dBm or power_W should be specified. (default: {dBm})')
    #parser.add_argument('-W', '--power_W', dest='power_W', type=float, default=W,
    #                    help=f'RF power [W] NOTE:One of power_dBm or power_W should be specified. (default: {W})')
    parser.add_argument('-i', '--ip_address', default=IP_ADDRESS, help=f'IP address of the AnaPico APSYN420 signal generator (default: {IP_ADDRESS})')
    parser.add_argument('--power', default=PORT, help=f'LAN Port of the AnaPico APSYN420 signal generator (default: {PORT})')
    parser.add_argument('-v', '--verbose', dest='verbose', default=0, type=int, help=f'Print out verbosity (default: 0)')
    args = parser.parse_args()

    if args.on == args.off:
        print('ERROR! Must select --on or --off')
    else:
        ret = main(
            onoff = args.on,
            freq = args.freq,
            ip_address = args.ip_address,
            verbose = args.verbose)
        pass
    pass
