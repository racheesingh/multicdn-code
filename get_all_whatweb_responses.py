import json
import subprocess

provider_name = raw_input("Enter CDN provider name (e.g.: msft_v4, msft_v6, apple): ")
with open("processed_metadata/rev_dns_mappings_%s.json" % provider_name) as fi:
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

with open("processed_metadata/ip_to_ww_%s.json" % provider_name, "w") as fi:
    json.dump(ip_to_ww, fi)

