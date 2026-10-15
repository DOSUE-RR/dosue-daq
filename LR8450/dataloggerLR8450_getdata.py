#!/bin/env python
import os, sys;
import signal;
import serial;
import DataLoggerLR8450;
from time import sleep;
import datetime;
from tzlocal import get_localzone;
import pytz;
 

DEVLOCATION = '192.168.0.3'; # NIFS experiment 2026/10/15
CHANNELS = ['UNIT1_CH1', 'UNIT1_CH2']
ISTEST   = False;

## setting for kill signal
def handler(signal, frame):
  print('Exit by kill signal')
  sys.exit(0)
  pass;
signal.signal(signal.SIGINT, handler)

if __name__ == '__main__':

  devlocation = DEVLOCATION;
  channels = CHANNELS;
  dt      = 60;
  verbose =  0;

  timezone = get_localzone();
  start    = datetime.datetime.now(timezone);

  # get arguments
  # argv[1] : output filename
  # argv[2] : devlocation 
  # argv[3] : channel list
  # argv[4] : time duration [sec]
  # argv[5] : verbose
  try:
      if len(sys.argv) < 2 or len(sys.argv) > 6: raise
      add = False
      if os.access(sys.argv[1], os.R_OK): add = True; # when continue to write
      if not os.path.isfile(sys.argv[1]): add = True; # when create a new file
      try:
        f = open(sys.argv[1], "a")
      except:
        print( 'Error!! Couldn\'t open file {}'.format(sys.argv[1]) );
        exit(1)
        pass;
      if(len(sys.argv) > 2): devlocation = sys.argv[2];
      if(len(sys.argv) > 3): channels    = (sys.argv[3]).split(',')
      if(len(sys.argv) > 4): dt          = float(sys.argv[4])
      if(len(sys.argv) > 5): verbose     = float(sys.argv[5])

      if verbose > 0 :
        print('devlocation = {}'.format(devlocation));
        print('dt          = {}'.format(dt        ));
        print('channels    = [{}]'.format(", ".join(channels)));
        print('verbose     = {}'.format(verbose   ));
        pass;

      if add :
        startStr = start.strftime('%Y/%m/%d %H:%M:%S:%f(%Z:%z)');
        line   = '# unix-time {} '.format(startStr);
        for ch in channels:
            line += f' <{ch} [V]>';
        f.write(line+'\n');
        f.flush();
        pass;
  except:
      print( 'Error!! Arguments were :');
      print(sys.argv);
      print( 'Error!! Usage: python dataloggerLR8450_getdata.py <output file> [<devlocation IP address or devfile path="192.168.0.3"> [<channels="U1-1,U1-2"> [<interval(sec) = 1 [<verbose>=0]]]]' );
      exit(1)
      pass

  ds = DataLoggerLR8450.DataLoggerLR8450(devlocation, channels=channels, verbose=verbose);
  if verbose > 1:
      print(f"LR8450 IDN = {ds.getIDN()}")
  # Get correct channel names
  channels = ds.channels;

  while True :
    voltages = ds.readValues(); # This function possibly takes some time.
    now      = datetime.datetime.now(timezone);

    # if AM/PM is different between now and start, the job is finished to change the output file.
    if (now.day) != (start.day) : break;

    line = '';
    line += '{}'.format(int(now.timestamp()));
    line += ' ';
    line += now.strftime('%Y/%m/%d %H:%M:%S:%f');
    try: 
        for ch in channels:
            line += ' {:f}'.format((float)(voltages[ch]));
    except Exception as e:
        print('Warning!! Invalid data obtained (error: {})! --> -1 filled'.format(e))
        line += ' -1';
        pass
    f.write(line+'\n');
    f.flush();
    if ISTEST : break;
    sleep(dt);

    pass; # end of while

  f.close();
  pass;
