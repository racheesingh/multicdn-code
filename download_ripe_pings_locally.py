import os
import sys
import pdb
from datetime import datetime
from ripe.atlas.cousteau import AtlasResultsRequest

ANALYSIS_DIR = "."

def get_raw_pings(destination="microsoft_v4", start=(2016, 01, 01), end=(2016, 02, 01)):
    if destination == "microsoft_v4":
        msm_id = 2240465
    elif destination == "microsoft_v6":
        msm_id = 2240487
    else:
        assert destination == "apple"
        msm_id = 1769099
    try:
        kwargs = {
            "msm_id": msm_id, 
            "start": datetime(start[0], start[1], start[2]),
            "stop": datetime(end[0], end[1], end[2])
            }
    except ValueError:
        return []
    is_success, results = AtlasResultsRequest(**kwargs).create()
    if is_success:
        return results
    else:
        return []

year = int(sys.argv[1])
for month in range(1, 13):
    if os.path.isfile(ANALYSIS_DIR + "/raw_data/msft_v4/%s/%s" % (year, month)):
        print "Exists", ANALYSIS_DIR + "/raw_data/msft_v4/%s/%s" % (year, month)
        continue
    fd = open(ANALYSIS_DIR + "/raw_data/msft_v4/%s/%s" % (year, month), "w")
    for day in range(1, 32):
        print "Year: %d, month: %d, day: %d" % (year, month, day)
        raw_msft_pings = get_raw_pings("microsoft_v4", (year,month,day), (year, month, day+1))
        print "Num pings", len(raw_msft_pings)
        if raw_msft_pings:
            for ping_mmt in raw_msft_pings:
                ts = str(ping_mmt['timestamp'])
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
                fd.write(",".join([ts, sent, rcvd, src_ip, dst_ip, min_rtt, max_rtt, avg_rtt]) + "\n")
    fd.close()
                         
