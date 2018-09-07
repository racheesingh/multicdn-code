from datetime import datetime
import time
import json
import pdb
import os
import csv

probe_uptime = {}
for year in [2015, 2016, 2017, 2018]:
    for month in range(1, 13):
        if os.path.getsize("/srv/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" %
                           (year, month)) == 0: continue
        print "year: %s, month: %s" % (year, month)
        with open("/srv/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" % (year, month)) as fi:
            reader = csv.reader(fi)
            for row in reader:
                if row[0] == 'ts': continue
                ts = int(row[0])
                rounded_down_hour = datetime.fromtimestamp(ts).replace(second=0, minute=0)
                rounded_down_hour_ts = int(time.mktime(rounded_down_hour.timetuple()))
                probe_id = int(row[-1])
                if probe_id not in probe_uptime:
                    probe_uptime[probe_id] = [rounded_down_hour_ts]
                else:
                    probe_uptime[probe_id].append(rounded_down_hour_ts)
probe_availability = {}
for probe in probe_uptime:
    uptimes = list(set(probe_uptime[probe]))
    fs = min(uptimes)
    ls = max(uptimes)
    uptime_hours = len(uptimes)
    lifetime_hours = float(ls - fs)/(60*60.0)
    print lifetime_hours, uptime_hours
    if lifetime_hours > 0:
        availability = uptime_hours/float(lifetime_hours)
    else:
        availability = 0
    if availability > 1: pdb.set_trace()
    probe_availability[probe] = availability
    
with open("processed_metadata/probe_availability_msft_v4.json", "w") as fi:
    json.dump(probe_availability, fi)
