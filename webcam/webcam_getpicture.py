#!/bin/env python3
import os, sys;
import subprocess;
import datetime;
import time;
import shutil;
import argparse

outdir0    = '/data1/dosue/webcam'
#dev_webcam = '/dev/v4l/by-id/usb-046d_Logitech_Webcam_C930e_4C3C897E-video-index0';
#dev_webcam = '/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera_SN0179-video-index0' # Tani's Chinese Camera
#dev_webcam = '/dev/video2' # FINER ELECOM_8MP_Webcam (Room)
dev_webcam = '/dev/video0' # FINER ELECOM_8MP_Webcam (Cryostat window)

# default setting
"""
Available Controls        Current Value   Range
------------------        -------------   -----
Brightness                128 (50%)       0 - 255
Contrast                  128 (50%)       0 - 255
Saturation                180 (70%)       0 - 255
White Balance Temperature, Auto True            True | False
Gain                      50 (19%)        0 - 255
Power Line Frequency      60 Hz           Disabled | 50 Hz | 60 Hz
White Balance Temperature 4738 (49%)      2000 - 7500
Sharpness                 120 (47%)       0 - 255
Backlight Compensation    0               0 - 1
Exposure, Auto            Aperture Priority Mode Manual Mode | Aperture Priority Mode
Exposure (Absolute)       333 (16%)       3 - 2047
Exposure, Auto Priority   True            True | False
Pan (Absolute)            0 (50%)         -36000 - 36000
Tilt (Absolute)           0 (50%)         -36000 - 36000
Focus (absolute)          35 (13%)        0 - 255
Focus, Auto               True            True | False
Zoom, Absolute            100 (0%)        100 - 400
Adjusting resolution from 384x288 to 352x288.
"""

nTimes = -1; # # of loop, -1: continue forever
#nTimes = 1; # # of loop, -1: continue forever
sleeptime  = 10; # sec
#width = 1920/2;
#height= 1080/2;
width = 3200/2;
height = 2400/2;
delay      =   0; #  option of fswebcam
frame      =   3; #  option of fswebcam
rotate     =   0; #  option(rotate) of fswebcam degrees
brightness = 128; #  0--255(default 128)
contrast   = 128; #  0--255(        128)
saturation = 128; #  0--255(        180)
redbalance =  32; # 24--40 (         32)
bluebalance=  32; # 24--40 (         32)
gamma      =  20; #  0--40 (         20)
sharpness  = 120; #  0--255(        120) 
#focusmode  = True # Focus, Auto   True or False( True)
focusmode  = False # Focus, Auto   True or False( True)
focus      =   0; #Focus (absolute)  0--255
zoom       = 100; # Zoom, Absolute 100--400

latestfilename = 'latest.jpg';

def getpicture(dev_webcam="/dev/video0", outdir='.', outname='aho.png', rotate=rotate) :
  #command = '/usr/bin/fswebcam {outdir}/{outname} -d {dev} -r {width}x{height} '.format(
  # The order of outname should be at last.
  #command = '/usr/bin/fswebcam --png 9 --jpeg 95 -d {dev} -F {frame} -D {delay} -r {width}x{height} --rotate {rotate} --set Brightness={brightness} --set Contrast={contrast} --set Saturation={saturation} --set "Red Balance={redbalance}" --set "Blue Balance={bluebalance}" --set Gamma={gamma} --set Sharpness={sharpness} --set "Focus, Auto={focusmode}" --set "Focus (absolute)={focus}" --set "Zoom, Absolute={zoom}" {outdir}/{outname}'.format(
  command = '/usr/bin/fswebcam --png -1 --jpeg -1  -d {dev} -F {frame} -D {delay} -r {width}x{height} --rotate {rotate} --set Brightness={brightness} --set Contrast={contrast} --set Saturation={saturation} --set "Red Balance={redbalance}" --set "Blue Balance={bluebalance}" --set Gamma={gamma} --set Sharpness={sharpness} --set "Focus, Auto={focusmode}" --set "Focus (absolute)={focus}" --set "Zoom, Absolute={zoom}" {outdir}/{outname}'.format(
  outdir=outdir, outname=outname, 
  dev=dev_webcam, frame=frame, delay=delay, 
  width =width , height =height , rotate=rotate,
  brightness=brightness, contrast=contrast, 
  saturation=saturation,  redbalance=redbalance, bluebalance=bluebalance,
  gamma=gamma, sharpness=sharpness, 
  focusmode=focusmode, focus=focus, zoom=zoom ); 
  print('command : {}'.format(command));
  output = subprocess.check_output( command , shell=True);
  print('output <--');
  print(output);
  print('-->');
  return 0;



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update', dest='updateOnlyLatest', default=1, type=int, help=f'(default: 1)')
    parser.add_argument('-f', '--focus', dest='focus', default=-1, type=int, help=f'(default: -1)')
    parser.add_argument('-d', '--device', dest='device', default="", type=str, help=f'(default: "")')
    parser.add_argument('-o', '--outdir', dest='outdir', default="", type=str, help=f'(default: "")')
    parser.add_argument('-r', '--rotate', dest='rotate', default=rotate, type=int, help=f'(default: {rotate})')
    args = parser.parse_args()

    updateOnlyLatest = args.updateOnlyLatest
    if args.focus >= 0:
        focusmode = False
        focus = args.focus
    else:
        focusmode = True
        pass
    
    if args.device != "":
        dev_webcam = args.device
        pass

    if args.outdir != "":
        outdir0 = args.outdir
        pass

    if args.rotate != rotate:
        rotate = args.rotate
        pass

    i = 0
    if nTimes < 0:
        i_max = 99
    else:
        i_max = nTimes
        pass
    while i < i_max:
        # get current time
        now    = datetime.datetime.now();
        # make latest picture
        getpicture( dev_webcam, outdir0, latestfilename, rotate );
 
        # copy file for ever keeping picture
        if not(updateOnlyLatest) : 
          nowStr  = now.strftime('%Y:%m:%d-%H:%M:%S');
          datedir = now.strftime('%Y%m%d');
          outdir = outdir0 + '/' + datedir ;
          if not os.path.isdir(outdir) :
              os.mkdir(outdir);
              pass;
          outname = '{}.jpg'.format( nowStr );
          print('time : {} --> copy file'.format(nowStr));
          shutil.copy2( '{}/{}'.format(outdir0,latestfilename), '{}/{}'.format(outdir,outname) );
          pass;
 
        # sleep
        if i != i_max-1 : time.sleep(sleeptime);
        if nTimes > 0:
            i += 1
            pass
        pass;
