import json
import pytz
import os
import sys
import pdb
from datetime import datetime
from ripe.atlas.cousteau import AtlasResultsRequest

destination_type = raw_input("Enter destination name (msft_v4, msft_v6, apple): ")
year = raw_input("Enter year for which data will be fetched (2015, 2016, 2017, 2018): ")
year = int(year.strip())
ANALYSIS_DIR = raw_input("Enter analysis directory to download files to: ")
if not os.path.exists(ANALYSIS_DIR + "/raw_data/%s" % destination_type):
    os.makedirs(ANALYSIS_DIR + "/raw_data/%s" % destination_type)

def get_raw_pings(destination="msft_v4", start=(2016, 01, 01)):
    if destination == "msft_v4":
        msm_id = 2240465
    elif destination == "msft_v6":
        msm_id = 2240487
    else:
        assert destination == "apple"
        msm_id = 1769099
    try:
        kwargs = {
            "msm_id": msm_id, 
            "start": datetime(start[0], start[1], start[2], 0,0, 0, 0, pytz.UTC),
            "stop": datetime(start[0], start[1], start[2], 23, 59, 59, 0, pytz.UTC)
            }
    except ValueError, e:
        print start, e
        return []
    is_success, results = AtlasResultsRequest(**kwargs).create()
    if is_success:
        return results
    else:
        return []

if os.path.isfile("processed_metadata/probe_uptime_%s.json" % destination_type):
    with open("processed_metadata/probe_uptime_%s.json" % destination_type) as fi:
        probe_uptime = json.load(fi)
else:
    probe_uptime = {}
    
for month in range(1, 13):
    if os.path.isfile(ANALYSIS_DIR + "/raw_data/%s/%s/%s" % (destination_type, year, month)):
        print "Exists", ANALYSIS_DIR + "/raw_data/%s/%s/%s" % (destination_type, year, month)
        continue
    fd = open(ANALYSIS_DIR + "/raw_data/%s/%s/%s" % (destination_type, year, month), "w")
    fd.write("ts, sent, recd, src, dst, min, max, avg, prb_id\n")
    for day in range(1, 32):
        print "Year: %d, month: %d, day: %d" % (year, month, day)
        raw_msft_pings = get_raw_pings(destination_type, (year,month,day))
        print "Num pings", len(raw_msft_pings)
        if raw_msft_pings:
            try:
                for  ping_mmt in raw_msft_pings:
                    ts = str(ping_mmt['timestamp'])
                    probe_id = str(ping_mmt['prb_id'])
                    if probe_id not in probe_uptime:
                        probe_uptime[probe_id] = {'fs': ts, 'ls': ts, 'uptime': 1}
                    else:
                        # Assumption is that the pings will be downloaded in
                        # the increasing order of year (2015, followed by 2016 and so on)
                        probe_uptime[probe_id]['ls'] = ts
                        probe_uptime[probe_id]['uptime'] += 1
                    sent = str(ping_mmt['sent'])
                    rcvd = str(ping_mmt['rcvd'])
                    min_rtt = str(ping_mmt['min'])
                    max_rtt = str(ping_mmt['max'])
                    avg_rtt = str(ping_mmt['avg'])
                    src_ip = ping_mmt['from']
                    if 'dst_addr' not in ping_mmt:
                        dst_ip = "DNS_FAIL"
                    else:
                        dst_ip = ping_mmt['dst_addr']
                    fd.write(",".join([ts, sent, rcvd,
                                       src_ip, dst_ip, min_rtt, max_rtt, avg_rtt, probe_id]) + "\n")
            except Exception as e:
                print "Error:", e
    fd.close()
                         
with open("processed_metadata/probe_uptime_%s.json" % destination_type, "w") as fi:
    json.dump(probe_uptime, fi)
