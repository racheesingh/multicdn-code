import pdb
import numpy as np
from api import *
from datetime import datetime
import time
import os
import csv
import json

fd = open("/nfs/kenny/data1/rachee/multicdn/processed_data/per_day_median.csv", "w")
per_ts_src_prefix = {}
per_ts_errors = {}
per_ts_dst_prefix = {}
for year in [2015, 2016, 2017, 2018]:
    per_day_median = {}
    for month in range(1, 13):
        if os.path.getsize("/nfs/kenny/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" %
                           (year, month)) == 0: continue
        print "year: %s, month: %s" % (year, month)
        with open("/nfs/kenny/data1/rachee/multicdn/raw_data/msft_v4/%s/%s" % (year, month)) as fi:
            reader = csv.reader(fi)
            for row in reader:
                ts = int(row[0])
                rounded_down_day = datetime.fromtimestamp(ts).replace(second=0, minute=0, hour=0)
                rounded_down_day_ts = int(time.mktime(rounded_down_day.timetuple()))
                recd = int(row[2])
                src_ip = row[3]
                dst_ip = row[4]
                rtt = float(row[5])
                if rtt < 0 : continue
                client_cc, _ = ip_to_cc(src_ip)
                if not client_cc:
                    client_ctn = 'Other'
                else:
                    try:
                        client_ctn = cc_to_ctn[client_cc]
                        client_ctn = cn_full_name[client_ctn]
                    except:
                        print "Could not resolve", client_cc
                        client_ctn = 'Other'
                if ts not in per_day_median:
                    per_day_median[ts] = {}
                if client_ctn not in per_day_median[ts]:
                    per_day_median[ts][client_ctn] = []
                per_day_median[ts][client_ctn].append(rtt)
    for ts in per_day_median:
        for ctn in per_day_median[ts]:
            fd.write(",".join([str(ts), str(ctn), str(np.median(per_day_median[ts][ctn]))]) + "\n")
fd.close()
