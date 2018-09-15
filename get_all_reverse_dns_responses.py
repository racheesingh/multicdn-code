import json
import socket
import pdb
import csv
provider_name = raw_input("Enter CDN provider name (e.g.: msft_v4, msft_v6, apple): ")
dirname = "/nfs/kenny/data1/rachee/multicdn/raw_data/%s/%d/%d"
rev_dns_mapping = {}
for year in [2015,2016,2017,2018]:
    for month in range(1,13):
        fname = dirname % (provider_name,year,month)
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
try: 
    with open("processed_metadata/rev_dns_mappings_%s.json" % provider_name, "w") as fi:
        json.dump(rev_dns_mapping, fi)
except:
    pdb.set_trace()
