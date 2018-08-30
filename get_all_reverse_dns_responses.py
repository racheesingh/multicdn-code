import json
import socket
import pdb
import csv

dirname = "/nfs/kenny/data1/rachee/multicdn/raw_data/msft_v4/%d/%d"
rev_dns_mapping = {}
for year in [2015,2016,2017,2018]:
    for month in range(1,13):
        fname = dirname % (year,month)
        with open(fname) as fi:
            reader = csv.reader(fi)
            for row in reader:
                dst_addr = row[4]
                if dst_addr == "DNS_FAIL": continue
                if dst_addr in rev_dns_mapping: continue
                try:
                    rev_dns = socket.gethostbyaddr(dst_addr)
                    rev_dns = rev_dns[0]
                except socket.herror:
                    rev_dns = None
                rev_dns_mapping[dst_addr] = rev_dns
                print dst_addr, rev_dns
            
with open("preprocessed_metadata/rev_dns_mappings.json", "w") as fi:
    json.dump(rev_dns_mapping, fi)
