# DOSUE-Y IF test at 4K
. /home/dosue/venv/env1/bin/activate
suffix=$1

# ON / 13.5 GHz
python3 ../APSYN420/APSYN420.py --on -f $((135*100000000))

sleep 2

# OFF
python3 ../APSYN420/APSYN420.py --off
