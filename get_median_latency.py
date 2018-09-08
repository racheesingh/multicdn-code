import random
import math
import pdb
import numpy as np
from api import *
from datetime import datetime
import time
import os
import csv
import json
provider_name = raw_input("Enter CDN provider name (e.g.: msft_v4, msft_v6, apple): ")
normalization = int(raw_input("0 for no normalizatiom, 1 for normalization based on eyeballs: "))
reliability_check = int(raw_input("Discard data from unreliable RIPE probes? 1 for Yes, 0 for No "))

DATA_DIR = raw_input("Enter directory that has provider traces: ")
fd = open("processed_metadata/per_day_median_%s_%d.csv" % (provider_name, normalization), "w")

def get_probes_from_metadata(fname):
    probe_to_asn = {}
    with open(fname) as fi:
        probe_meta = json.load(fi)
    for pr in probe_meta['objects']:
        if not pr['asn_v4']: continue
        probe_to_asn[int(pr['id'])] = pr['asn_v4']
    return probe_to_asn

probe_to_asn  = get_probes_from_metadata("/nfs/kenny/data1/rachee/pathcache/20180828.json")
TOTAL_EYEBALLS = 3463872804
with open("processed_metadata/asn_to_num_users.json") as fi:
    asn_to_eyeballs = json.load(fi)

def get_fraction(client_asn):
    if str(client_asn) in asn_to_eyeballs:
        frac = asn_to_eyeballs[str(client_asn)]/float(TOTAL_EYEBALLS)
    else:
        frac = 0
    assert frac <= 1
    return frac
    
per_ts_src_prefix = {}
per_ts_errors = {}
per_ts_dst_prefix = {}
for year in [2015, 2016, 2017, 2018]:
    per_day_median = {}
    for month in range(1, 13):
        if os.path.getsize("%s/raw_data/%s/%s/%s" %
                           (DATA_DIR, provider_name, year, month)) == 0: continue
        print "year: %s, month: %s" % (year, month)
        with open("%s/raw_data/%s/%s/%s" %
                  (DATA_DIR, provider_name, year, month)) as fi:
            reader = csv.reader(fi)
            for row in reader:
                if row[0] == 'ts': continue
                ts_raw = int(row[0])
                rounded_down_day = datetime.fromtimestamp(ts_raw).replace(second=0,
                                                                      minute=0, hour=0, day=1)
                rounded_down_day_ts = int(time.mktime(rounded_down_day.timetuple()))
                recd = int(row[2])
                src_ip = row[3]
                dst_ip = row[4]
                rtt = float(row[5])
                if rtt < 0 : continue
                probe_id = int(row[-1])
                if probe_id in probe_to_asn:
                    client_asn = int(probe_to_asn[probe_id])
                else:
                    client_asn = ip2asn_bgp(src_ip)
                    if not client_asn:
                        print src_ip
                        client_asn = 'none'
                    else:
                        client_asn = int(client_asn)
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
                if rounded_down_day_ts not in per_day_median:
                    per_day_median[rounded_down_day_ts] = {}
                if client_ctn not in per_day_median[rounded_down_day_ts]:
                    per_day_median[rounded_down_day_ts][client_ctn] = {}
                if client_asn not in per_day_median[rounded_down_day_ts][client_ctn]:
                    per_day_median[rounded_down_day_ts][client_ctn][client_asn] = []
                per_day_median[rounded_down_day_ts][client_ctn][client_asn].append(rtt)
    if normalization:
        normalized_per_day_median = {}
        for ts in per_day_median:
            normalized_per_day_median[ts] ={}
            for client_ctn in per_day_median[ts]:
                selected_pings = []
                for client_asn in per_day_median[ts][client_ctn]:
                    num_select = math.ceil(get_fraction(client_asn) * \
                                 len(per_day_median[ts][client_ctn][client_asn]))
                    if num_select == 0:
                        num_select = len(per_day_median[ts][client_ctn][client_asn])
                    try:
                        num_select = int(num_select)
                        sampled_pings = \
                                        random.sample(per_day_median[ts][client_ctn][client_asn], num_select)
                    except:
                        pdb.set_trace()
                    selected_pings.extend(sampled_pings)
                normalized_per_day_median[ts][client_ctn] = selected_pings
        per_day_median = normalized_per_day_median
        
    for ts in per_day_median:
        for ctn in per_day_median[ts]:
            fd.write(",".join([str(ts), str(ctn), str(np.median(per_day_median[ts][ctn]))]) + "\n")
fd.close()
