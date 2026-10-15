#!/bin/env python
import os, sys;
import datetime;
       
this_dir = os.path.dirname(os.path.abspath(__file__))
run_script = '{}/dataloggerLR8450_getdata.py'.format(this_dir);
outdirectory = '/data3/dosue/dosue-axion/data/dataLoggerLR8450'
devlocation = "192.168.0.3" # IP address or USB devfile
channels = 'CH1_1,CH1_2,CH1_3,CH1_4'
dt = 10; # data aqcuisition period [sec]

if __name__ == '__main__':

  isTest = False;
  if len(sys.argv)>1 : isTest = True;

  now = datetime.datetime.now();
  nowStr = now.strftime('%Y-%m-%d');
  outputfilename = '{}/data_{}.dat'.format( outdirectory, nowStr );
  cmd = r'python {} {} {} {} {}'.format( run_script, outputfilename, devlocation, channels, dt );
  print(cmd);
  if not isTest : os.system( cmd );

  pass;
