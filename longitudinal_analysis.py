from api import *
import time
import os
import csv
import json
import pdb
from datetime import datetime
import sys

granularity = sys.argv[1]

def get_src_dst(ip_addr, granularity="ip"):
    if granularity == "ip": return ip_addr
    if granularity == "pfx": return ip_to_pref(ip_addr)
    if granularity == "asn": return ip2asn_bgp(ip_addr)
    
per_src_dst_ts_rtt = {}
for year in [2015, 2016, 2017, 2018]:
    for month in range(1, 13):
        if os.path.getsize("msft_v4/%s/%s" % (year, month)) == 0: continue
        print "year: %s, month: %s" % (year, month)
        with open("msft_v4/%s/%s" % (year, month)) as fi:
            reader = csv.reader(fi)
            for row in reader:
                ts = int(row[0])
                rounded_down_hour = datetime.fromtimestamp(ts).replace(second=0, minute=0)
                rounded_down_hour_ts = int(time.mktime(rounded_down_hour.timetuple()))
                recd = int(row[2])
                if recd < 0: continue
                src_ip = row[3]
                dst_ip = row[4]
                rtt = row[5]
                src = get_src_dst(src_ip, granularity=granularity)
                dst = get_src_dst(dst_ip, granularity=granularity)
                if "%s-%s" % (src, dst) not in per_src_dst_ts_rtt:
                    per_src_dst_ts_rtt["%s-%s" % (src, dst)] = {}
                if rounded_down_hour_ts not in per_src_dst_ts_rtt["%s-%s" % (src, dst)]:
                    per_src_dst_ts_rtt["%s-%s" % (src, dst)][rounded_down_hour_ts] = []
                per_src_dst_ts_rtt["%s-%s" % (src, dst)][rounded_down_hour_ts].append(rtt)
                

with open("per_src_dst_ts_rtt_%s.json" % granularity, "w") as fi:
    json.dump(per_src_dst_ts_rtt, fi)