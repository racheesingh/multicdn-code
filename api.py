import radix
from datetime import datetime
import os
import csv
import json
import geoip2.database

rtree_bgpv4 = radix.Radix()
asn_to_prefs = {}
with open("data/routeviews-rv2-20180218-1200.pfx2as") as fi:
    for line in fi:
        ip, preflen, asn = line.split()
        if asn in asn_to_prefs:
            asn_to_prefs[asn].append("%s/%s" % (ip, preflen))
        else:
            asn_to_prefs[asn] = ["%s/%s" % (ip, preflen)]
        if ',' in asn:
            tokens = asn.split(',')
            asn = tokens[0]
        if '_' in asn:
            tokens = asn.split('_')
            asn = tokens[0]
        rnode = rtree_bgpv4.add(network=ip, masklen=int(preflen))
        rnode.data["asn"] = asn
        
rtree_bgpv6 = radix.Radix()
asn6_to_prefs = {}
with open("data/routeviews-rv6-20180218-1200.pfx2as") as fi:
    for line in fi:
        ip, preflen, asn = line.split()
        if asn in asn6_to_prefs:
            asn6_to_prefs[asn].append("%s/%s" % (ip, preflen))
        else:
            asn6_to_prefs[asn] = ["%s/%s" % (ip, preflen)]
        if ',' in asn:
            tokens = asn.split(',')
            asn = tokens[0]
        if '_' in asn:
            tokens = asn.split('_')
            asn = tokens[0]
        rnode = rtree_bgpv6.add(network=ip, masklen=int(preflen))
        rnode.data["asn"] = asn
        
def ip2asn_bgp(ip, v6=False):
    if v6:
        try:
            node = rtree_bgpv6.search_best(ip)
        except ValueError:
            print "Could not get AS for IP", ip
            return None
    else:
        try:
            node = rtree_bgpv4.search_best(ip)
        except ValueError:
            print "Could not get AS for IP", ip
            return None
    if node:
        return node.data['asn']
    else:
        return None
    
def ip_to_pref(ip):
    try:
        node = rtree_bgpv4.search_best(ip)
    except ValueError:
        print "Could not get prefix for IP", ip
        return None

    if node:
        return node
    else:
        return None

cc_to_ctn = {}
with open("data/country_continent.csv") as fi:
    reader = csv.reader(fi)
    for row in reader:
        cc_to_ctn[row[0]] = row[1]
cc_to_ctn['CW'] = 'SA'
cc_to_ctn['SS'] = 'AF'

with open("data/asn_to_cc") as fi:
    asn_to_cc = json.load(fi)

reader = geoip2.database.Reader('GeoLite2-Country_20171107/GeoLite2-Country.mmdb')

def ip_to_cc(ip):
    try:
        response = reader.country(ip)
    except:
        return None, None
    if not response:
        return None, None
    return response.country.iso_code, response.country.name
cn_full_name = {'NA': "North America", "AS": "Asia", "OC": "Oceania",
                "AF": "Africa", "EU": "Europe", "SA": "South America",
                "None": "None"}

orgs = {}
orgs_info = {}
with open("data/20161001.as-org2info.txt", "rb") as f:
    for line in f:
        # ignore commented lines
        if line[0] == "#":
            continue
        tokens = line.rstrip().split('|')
        # aut|changed|name|org_id|source
        if tokens[0].isdigit():
            asn = int(tokens[0])
            # asn to org id
            orgs[asn] = tokens[3]
        else:
            # org ID to name and CN
            orgs_info[tokens[0]] = (tokens[2], tokens[3])

def get_asn_family(family_name="microsoft"):
    orgs_ids_names = [(x[0], x[1][0]) for x in orgs_info.items()]
    match_org_ids = [x[0] for x in orgs_ids_names if family_name in x[1].lower()]
    return match_org_ids

popular_cdns = {'microsoft', 'akamai', 'amazon', 'limelight', 'cdnetworks', 'bitgravity',
                'google', 'chinacache'}
popcdn_cache = {}
def is_popcdn(dst_asn):
    if not dst_asn: return False
    if dst_asn == 'None': return False
    if dst_asn in popcdn_cache:
        return popcdn_cache[dst_asn]
    if int(dst_asn) not in orgs:
        return False
    org_id = orgs[int(dst_asn)]
    for popcdn in popular_cdns:
        popcdn_org_ids = get_asn_family(popcdn)
        for porgid in popcdn_org_ids:
            if org_id == porgid:
                popcdn_cache[dst_asn] = popcdn.capitalize() + ', ' + orgs_info[org_id][1]
                return popcdn.capitalize() + ', ' + orgs_info[org_id][1]
    popcdn_cache[dst_asn] = False
    return False

with open("processed_metadata/rev_dns_mappings.json") as fi:
    rev_dns_map = json.load(fi)

with open("processed_metadata/ip_to_ww.json") as fi:
    ww_map = json.load(fi)

def get_reverse_dns_map(provider="msft_v4"):
    if provider == 'msft_v4':
        with open("processed_metadata/rev_dns_mappings.json") as fi:
            rev_dns_map = json.load(fi)
    else:
        assert provider == 'apple'
        with open("processed_metadata/rev_dns_mappings_apple.json") as fi:
            rev_dns_map = json.load(fi)
    return rev_dns_map

def get_ww_map(provider="msft_v4"):
    if provider == 'msft_v4':
        with open("processed_metadata/ip_to_ww.json") as fi:
            ww_map = json.load(fi)
    else:
        assert provider == 'apple'
        with open("processed_metadata/ip_to_ww.json") as fi:
            ww_map = json.load(fi)

dst_asn_to_edgecache_mapping = {}   
dst_asn_to_edgecache_mapping_failed = {}
def check_if_edgecache(src_asn, dst_ip):
    is_ec = False
    typ_ec = None
    rev_dns_hostname = rev_dns_map[dst_ip]
    if not rev_dns_hostname:
        if dst_ip in ww_map:
            ww_hostname = ww_map[dst_ip]
        else:
            ww_hostname = None

    dst_asn = ip2asn_bgp(dst_ip)
    if src_asn == dst_asn:
        is_ec = True
    
    elif dst_asn in probes_per_asn and probes_per_asn[dst_asn]:
        # If destination ASN hosts a non-anchoring RIPE probe, this
        # destination AS is likely an edge cache. Accuracy of this
        # heuristic, we don't know
        is_ec = True
    # Does the reverse DNS hostname say something?
    # Since at this point we know this AS is neither MSFT nor
    # popular CDNs, if we hit these keywords, we have
    # hit an edgecache.
    if rev_dns_hostname and 'akamai' in rev_dns_hostname:
        is_ec = True
        typ_ec = "Akamai"
    elif rev_dns_hostname and 'msedge' in rev_dns_hostname:
        is_ec = True
        typ_ec = "Microsoft"
    elif rev_dns_hostname and 'aws' in rev_dns_hostname:
        is_ec = True
        typ_ec = "Amazon"
    elif rev_dns_hostname and "google" in rev_dns_hostname:
        is_ec = True
        typ_ec = "Google"
    else:
        if dst_ip in dst_ip_to_hostname_whatweb:
            typ_ec = dst_ip_to_hostname_whatweb[dst_ip]
            if typ_ec:
                is_ec = True
        else:
            if typ == 'msft_v6':
                output = None
            else:
                output = subprocess.check_output(["./WhatWeb/whatweb", dst_ip])
            if output:
                if "AkamaiGHost" in output:
                    typ_ec = "Akamai"
                    is_ec = True
                    dst_ip_to_hostname_whatweb[dst_ip] = typ_ec
                elif 'aws' in output.lower():
                    is_ec = True
                    typ_ec = "Amazon"
                    dst_ip_to_hostname_whatweb[dst_ip] = typ_ec
                elif 'msedge' in output.lower():
                    is_ec = True
                    typ_ec = "Microsoft"
                    dst_ip_to_hostname_whatweb[dst_ip] = typ_ec
                elif 'google' in output.lower():
                    is_ec = True
                    typ_ec = "Google"
                    dst_ip_to_hostname_whatweb[dst_ip] = typ_ec
                else:
                    dst_ip_to_hostname_whatweb[dst_ip] = None
                    print dst_ip, output

    # Giving up now, its not an edge cache or we have no good way of
    # finding if it is.
    if not is_ec:
        print "Not an edge cache", dst_asn, rev_dns_hostname
        if typ_ec:
            print "MADNESS", typ_ec
        if dst_asn not in dst_asn_to_edgecache_mapping_failed:
            dst_asn_to_edgecache_mapping_failed[dst_asn] = 1
        else:
            dst_asn_to_edgecache_mapping_failed[dst_asn] += 1
        return is_ec, typ_ec

    if not typ_ec:
        # No clean edgecache name, will call it with the ASN + CC
        if int(dst_asn) in orgs:
            typ_ec = ", ".join(orgs_info[orgs[int(dst_asn)]])
    else:
        try:
            if int(dst_asn) in orgs:
                typ_ec = typ_ec + ", " + orgs_info[orgs[int(dst_asn)]][1]
        except UnicodeDecodeError:
            pdb.set_trace()
            
    if dst_asn not in dst_asn_to_edgecache_mapping:
        dst_asn_to_edgecache_mapping[dst_asn] = typ_ec
    print "Edgecache:", typ_ec
    return is_ec, typ_ec

def pick_preferable_dst_name(x, y):
    wellknown_names = ['Akamai', 'Microsoft', 'Google', 'Amazon']
    x_name = None
    y_name = None
    for wkn in wellknown_names:
        if wkn.lower() in x.lower():
            x_name = wkn
        if wkn.lower() in y.lower():
            y_name = wkn

    if x_name and y_name:
        # WTF
        print x_name, y_name
        if len(x_name) < len(y_name):
            return x
        else:
            return y
    elif x_name:
        return x
    else:
        return y
