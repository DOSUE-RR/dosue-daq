#!/bin/bash
/usr/bin/flock -x --timeout 10 /home/dosue/dosue/dosue-daq/webcam/cronwebcam_cryostat.lock -c ". /home/dosue/venv/env1/bin/activate; python3 /home/dosue/dosue/dosue-daq/webcam/webcam_getpicture.py -u 0 -r 90 -d /dev/video0 -o /data1/dosue/finer/webcam_cryostat" 2>&1> /home/dosue/dosue/dosue-daq/webcam/webcam_log_cryostat.out
