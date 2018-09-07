import json
import pdb
import os
import time

f = open("data/aspop.html")
total_users = 0
as_to_users = {}
for table in f:
    records = table.split("[")
    for record in records:
        record = record.split("]")[0]
        if 'AS Name' in record: continue
        try:
            asn = record.split(",")[1].strip("\"").split('AS')[-1]
            num_users = int(record.split(",")[-4])
            print asn, num_users
            total_users += num_users
            as_to_users[asn] = num_users
        except IndexError:
            continue
f.close()

with open("processed_metadata/asn_to_num_users.json", "w") as fi:
    json.dump(as_to_users, fi)
    
print "total users", total_users
# 3463872804
