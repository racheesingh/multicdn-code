# multicdn-code
## Purpose of code files
1. `download_ripe_pings_locally.py`: downloads pings from all RIPE Atlas probes to Microsoft Windows update URL (both v4 and v6) and Apple iOS update URL into a local directory (specificed at runtime).
2. `get_all_reverse_dns_responses.py`: does a reverse DNS lookup on all server IP addresses hosting OS updates found in the DNS resolution of Windows/Apple update URL from all available RIPE Atlas probes.
3. `get_all_whatweb_responses.py`: DNS resolution for a number of IP addreses fails, for these, this script does a WhatWeb lookup to identify the type of server hosting content.
4. `get_basic_stats.py`: first cut analysis of the number of active client and server prefixes observed per day from 2015 to 2018.
5. `get_median_latency.py`: keeps median latency of per day for each continent during the analysis perfiod.
