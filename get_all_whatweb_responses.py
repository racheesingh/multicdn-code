import json
import subprocess
with open("preprocessed_metadata/rev_dns_mappings.json") as fi:
    ip_to_rev_dns = json.load(fi)

ip_to_ww = {}
for ip in ip_to_rev_dns:
    if ip_to_rev_dns[ip]: continue
    output = subprocess.check_output(["./WhatWeb/whatweb", ip])
    if output:
        if "AkamaiGHost" in output:
            typ_ec = "Akamai"
        elif 'aws' in output.lower():
            typ_ec = "Amazon"
        elif 'msedge' in output.lower():
            typ_ec = "Microsoft"
        elif 'google' in output.lower():
            typ_ec = "Google"
        elif "cloudflare" in output.lower():
            typ_ec = "CloudFlare"
        else:
            print "NOT FOUND:", ip, output
            continue
        print "FOUND:", ip, typ_ec
        ip_to_ww[ip] = typ_ec

with open("ip_to_ww.json", "w") as fi:
    json.dump(ip_to_ww, fi)

