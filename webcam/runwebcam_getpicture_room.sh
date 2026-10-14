#!/bin/bash
/usr/bin/flock -x --timeout 10 /home/dosue/dosue/dosue-daq/webcam/cronwebcam_room.lock -c ". /home/dosue/venv/env1/bin/activate; python3 /home/dosue/dosue/dosue-daq/webcam/webcam_getpicture.py -u 0 -d /dev/video2 -o /data1/dosue/finer/webcam_room" 2>&1> /home/dosue/dosue/dosue-daq/webcam/webcam_log_room.out
