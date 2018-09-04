import pytz
import pdb
'''
Gets basic statistics about the data:
1. Get number of unique prefixes (both client and server) per day for each continenet
'''
from api import *
from datetime import datetime
import time
import os
import csv
import json

per_ts_src_prefix = {}
per_ts_errors = {}
per_ts_dst_prefix = {}
for year in [2015]:
# for year in [2015, 2016, 2017, 2018]:
    for month in range(1, 13):
        if os.path.getsize("/nfs/kenny/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" %
                           (year, month)) == 0: continue
        print "year: %s, month: %s" % (year, month)
        with open("/nfs/kenny/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" % (year, month)) as fi:
            reader = csv.reader(fi)
            for row in reader:
                ts = int(row[0])
                rounded_down_day = datetime.fromtimestamp(ts,
                                            tz=pytz.UTC).replace(second=0, minute=0, hour=0)
                rounded_down_day_ts = int(time.mktime(rounded_down_day.timetuple()))
                recd = int(row[2])
                src_ip = row[3]
                dst_ip = row[4]
                src_pref = '.'.join(src_ip.split('.')[:-1] + ['0'])
                dst_pref = '.'.join(dst_ip.split('.')[:-1] + ['0'])
                if recd < 0:
                    if rounded_down_day_ts not in per_ts_errors:
                        per_ts_errors[rounded_down_day_ts] = []
                    per_ts_errors[rounded_down_day_ts].append(src_pref)
                if rounded_down_day_ts not in per_ts_src_prefix:
                    per_ts_src_prefix[rounded_down_day_ts] = []
                per_ts_src_prefix[rounded_down_day_ts].append(src_pref)
                if rounded_down_day_ts not in per_ts_dst_prefix:
                    per_ts_dst_prefix[rounded_down_day_ts] = []
                per_ts_dst_prefix[rounded_down_day_ts].append(dst_pref)

src_ctn_pfx_counts= [["ts", "ctn", "count"]]
for ts in sorted(per_ts_src_prefix.keys()):
    per_ctn_counts = {}
    src_prefix_set = list(set(per_ts_src_prefix[ts]))
    print ts
    for pref in src_prefix_set:
        client_cc, _ = ip_to_cc(pref)
        if not client_cc:
            client_ctn = 'Other'
        else:
            try:
                client_ctn = cc_to_ctn[client_cc]
                client_ctn = cn_full_name[client_ctn]
            except:
                print "Could not resolve", client_cc
                client_ctn = 'Other'
        if client_ctn not in per_ctn_counts:
            per_ctn_counts[client_ctn] = 0
        per_ctn_counts[client_ctn] += 1
    for ctn in per_ctn_counts:
        src_ctn_pfx_counts.append([ts, ctn, per_ctn_counts[ctn]])
    
with open("/nfs/kenny/data1/rachee/multicdn/processed_data/per_src_ctn_pfx_counts.csv", "w") as fi:
    writer = csv.writer(fi)
    writer.writerows(src_ctn_pfx_counts)

dst_ctn_pfx_counts = [["ts", "ctn", "count"]]
for ts in per_ts_dst_prefix:
    per_ctn_counts = {}
    dst_prefix_set = list(set(per_ts_dst_prefix[ts]))
    for pref in dst_prefix_set:
        server_cc, _ = ip_to_cc(pref)
        if not server_cc:
            server_cc = 'Other'
        else:
            server_ctn = cc_to_ctn[server_cc]
            server_ctn = cn_full_name[server_ctn]
        if server_ctn not in per_ctn_counts:
            per_ctn_counts[server_ctn] = 0
        per_ctn_counts[server_ctn] += 1
    for ctn in per_ctn_counts:
        dst_ctn_pfx_counts.append([ts, ctn, per_ctn_counts[ctn]])

with open("/nfs/kenny/data1/rachee/multicdn/processed_data/per_dst_ctn_pfx_counts.csv", "w") as fi:
    writer = csv.writer(fi)
    writer.writerows(dst_ctn_pfx_counts)
    
